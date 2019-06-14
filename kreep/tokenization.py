#---------------------------------------------------------------
# kreep - keystroke recognition and entropy elimination program
#   by Vinnie Monaco
#   www.vmonaco.com
#   contact AT vmonaco DOT com
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

import numpy as np
import pandas as pd


def google_detect_space(df):
    d = df['frame_length'].diff().fillna(0).astype(int)

    if len(d) >= 10:
        d.iloc[9] -= 1

    space = (d == 2)|(d == 3)
    return space


def baidu_detect_space(df):
    d = df['frame_length'].diff().fillna(0).astype(int)

    if len(d) >= 10:
        d.iloc[9] -= 1

    space = (d == 4)

    if d.iloc[1] == 9:
        space.iloc[1] = True

    return space


def detect_space(df, website, max_word_length):
    detect_space_rules = {
        'google': google_detect_space,
        'baidu': baidu_detect_space
    }

    df = df.copy()
    df['cp'] = np.arange(1, len(df)+1)
    df['predict_space'] = detect_space_rules[website](df)

    # No spaces at begin/end
    df.iloc[0, df.columns.get_loc('predict_space')] = False
    df.iloc[-1, df.columns.get_loc('predict_space')] = False

    # No consecutive spaces, keep first
    reset = df['predict_space'].astype(int).diff() > 0
    cumsum = reset.cumsum()
    rolling_space = df['predict_space'].groupby(reset.cumsum()).cumsum()
    df['predict_space'] = df['predict_space'] & ((rolling_space % 2) == 1)

    word_lengths = lambda x: x.groupby(x.cumsum()).apply(lambda y: (~y).sum())

    def split_word(x):
        '''
        For tokens longer than any dictionary word, try to split the token by
        recovering a false negative due to (in this order):
            * cp changing from 9 to 10
            * difference greater than 2
            * difference less than 0
            * largest packet interval-arrival time
        '''
        space = x['predict_space']

        if (~space).sum() > MAX_WORD_LENGTH:
            d = x['frame_length'].diff()[1:-1]

            if 10 in x['cp'].values[1:-1]:
                idx = (x['cp']==10).idxmax()
            elif (d >= 2).any():
                idx = d.idxmax()
            elif (d < 0).any():
                idx = d.idxmin()
            else:
                dt = x['frame_time'].diff().shift(-1)[1:-1]
                idx = dt.idxmax()

            x.loc[idx, 'predict_space'] = True

        return x

    while word_lengths(df['predict_space']).max() > max_word_length:
        df = df.groupby(df['predict_space'].cumsum()).apply(split_word)

    return df['predict_space']


def tokenize_words(df, website, max_word_length):
    space = detect_space(df, website, max_word_length)

    # Tokenize sequence with trailing spaces
    return space.shift().fillna(False).cumsum()
