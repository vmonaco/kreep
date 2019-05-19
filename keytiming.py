import string
import numpy as np
import pandas as pd
from scipy import stats

KEYS = list(string.ascii_lowercase) + [' ']

BIGRAMS = pd.read_csv('bigrams.csv', index_col=[0,1])

def word_proba(x, word):
    lp = 0
    for i in range(len(word)-1):
        key1 = word[i]
        key2 = word[i+1]

        if (key1,key2) not in BIGRAMS.index:
            obs = []

            if key1 in BIGRAMS.index.levels[0]:
                obs.append(BIGRAMS.xs(key1, level=0))

            if key2 in BIGRAMS.index.levels[1]:
                obs.append(BIGRAMS.xs(key2, level=1))

            if not len(obs):
                obs = [BIGRAMS]

            obs = pd.concat(obs, ignore_index=True)

            mean = obs['mean'].mean()
            std = obs['std'].mean()
        else:
            mean = BIGRAMS.loc[(key1,key2), 'mean']
            std = BIGRAMS.loc[(key1,key2), 'std']

        p = stats.norm.pdf(x[i], loc=mean, scale=std)
        lp += np.log(p)

    return lp

def keystroke_timing(keystrokes, words):
    word_probas = []
    keystrokes['latency'] = keystrokes['frame_time'].diff()*1000
    _, latency = zip(*keystrokes.groupby('token')['latency'])

    latency = list(latency)
    for i in range(len(latency)-1):
        latency[i] = latency[i].values[1:-1]

    latency[-1] = latency[-1].values[1:]

    for x, words_i in zip(latency, words):
        df = pd.Series([word_proba(x, w) for w in words_i], index=words_i)
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
