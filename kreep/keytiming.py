#---------------------------------------------------------------
# kreep - keystroke recognition and entropy elimination program
#   by Vinnie Monaco
#   www.vmonaco.com
#   contact AT vmonaco DOT com
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

import string
import numpy as np
import pandas as pd
from scipy import stats

KEYS = list(string.ascii_lowercase) + [' ']


def word_proba(bigrams, x, word):
    lp = 0
    for i in range(len(word)-1):
        key1 = word[i]
        key2 = word[i+1]

        if (key1,key2) not in bigrams.index:
            obs = []

            if key1 in bigrams.index.levels[0]:
                obs.append(bigrams.xs(key1, level=0))

            if key2 in bigrams.index.levels[1]:
                obs.append(bigrams.xs(key2, level=1))

            if not len(obs):
                obs = [bigrams]

            obs = pd.concat(obs, ignore_index=True)

            mean = obs['mean'].mean()
            std = obs['std'].mean()
        else:
            mean = bigrams.loc[(key1,key2), 'mean']
            std = bigrams.loc[(key1,key2), 'std']

        p = stats.norm.pdf(x[i], loc=mean, scale=std)
        lp += np.log10(p)

    return lp


def keystroke_timing(bigrams, keystrokes, words):
    word_probas = []
    keystrokes['latency'] = keystrokes['frame_time'].diff()
    _, latency = zip(*keystrokes.groupby('token')['latency'])

    latency = list(latency)
    for i in range(len(latency)-1):
        latency[i] = latency[i].values[1:-1]

    latency[-1] = latency[-1].values[1:]

    for x, words_i in zip(latency, words):
        df = pd.Series([word_proba(bigrams, x, w) for w in words_i], index=words_i)
        word_probas.append(df)

    return word_probas


def train_model(fname_in, fname_out, time_col='press_time', key_col='key_name', groupby=['user','session']):
    df = pd.read_csv(fname_in)

    df = df.sort_values(groupby + [time_col])

    df[key_col] = df[key_col].replace({'space':' '})

    df['1st_key'] = df.groupby(groupby)[key_col].shift(1)
    df['2nd_key'] = df[key_col]
    df['latency'] = df.groupby(groupby)[time_col].diff()

    df = df.dropna()

    df = df[df['1st_key'].isin(KEYS) & df['2nd_key'].isin(KEYS)]

    df = df.groupby(['1st_key','2nd_key']).filter(lambda x: len(x) >= 5)

    fits = df.groupby(['1st_key','2nd_key'])['latency'].agg([np.mean, np.std])

    fits.to_csv(fname_out)


if __name__ == '__main__':
    import sys
    train_model(sys.argv[1], sys.argv[2])
