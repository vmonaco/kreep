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
from itertools import product

# Length of each symbol in the Huffman code used in HPACK
huffman_lengths = [
13, 23, 28, 28, 28, 28, 28, 28, 28, 24, 30, 28, 28, 30, 28, 28,
28, 28, 28, 28, 28, 28, 30, 28, 28, 28, 28, 28, 28, 28, 28, 28,
6, 10, 10, 12, 13, 6, 8, 11, 10, 10, 8, 11, 8, 6, 6, 6,
5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 7, 8, 15, 6, 12, 10,
13, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
7, 7, 7, 7, 7, 7, 7, 7, 8, 7, 8, 13, 19, 13, 14, 6,
15, 5, 6, 5, 6, 5, 6, 6, 6, 5, 7, 7, 6, 6, 6, 5,
6, 7, 6, 5, 5, 6, 7, 7, 7, 7, 7, 15, 11, 14, 13, 28,
20, 22, 20, 20, 22, 22, 22, 23, 22, 23, 23, 23, 23, 23, 24, 23,
24, 24, 22, 23, 24, 23, 23, 23, 23, 21, 22, 23, 22, 23, 23, 24,
22, 21, 20, 22, 22, 23, 23, 21, 23, 22, 22, 24, 21, 22, 23, 23,
21, 21, 22, 21, 23, 22, 23, 23, 20, 22, 22, 22, 23, 22, 22, 23,
26, 26, 20, 19, 22, 23, 22, 25, 26, 26, 26, 27, 27, 26, 24, 25,
19, 21, 26, 27, 27, 26, 27, 24, 21, 21, 26, 26, 28, 27, 27, 27,
20, 24, 20, 21, 22, 21, 21, 23, 22, 22, 25, 25, 24, 24, 26, 23,
26, 27, 26, 26, 27, 27, 27, 27, 27, 28, 27, 27, 27, 27, 27, 26,
]

def huffman(c):
    return huffman_lengths[ord(c)]

char2huflen = {k:huffman(k) for k in string.ascii_lowercase+string.digits}


def choose_first_last(d, cp_start):
    '''
    Attempt to use size patterns with anomalies.
    If the sequence contains size differences < 0 or > 2, use the subsequence
    before or after the anomaly (whichever is longer).
    '''
    d = pd.Series(d)
    ok = (d >= 0) & (d <= 1)

    cp = np.arange(cp_start, cp_start+len(d))
    if 10 in cp:
        idx10 = ok[cp==10].idxmax()
        if d.loc[idx10] == 2:
            ok.loc[idx10] = True

    if ok.sum() == 0:
        return 0, len(d)

    groups = (~ok).cumsum()
    groups = groups[ok]
    s = groups.groupby(groups).size()

    group_idx = s.idxmax()
    biggest = groups[groups==group_idx]
    first, last = biggest.index.min(), biggest.index.max()+1

    return first, last


def incremental_compression(words, byte_pattern, cp_start):
    '''
    Determine the probability of each word given an observed frame length
    difference pattern and a guess for the first cp parameter
    '''
    n = len(byte_pattern)

    first, last = choose_first_last(np.array(byte_pattern).astype(int), cp_start)

    byte_pattern = '_'.join(byte_pattern[first:last])

    cp_size = lambda cp: sum(char2huflen[c] for c in str(cp))
    cp_sizes = np.array([cp_size(cp) for cp in range(cp_start, cp_start+n)])

    prev_size = pd.DataFrame(cp_size(cp_start-1)*np.ones(len(words), dtype=int), columns=[-1], index=words.index)
    size_with_cp = pd.concat([prev_size, words.cumsum(axis=1)+cp_sizes], axis=1)

    def make_patterns(x):
        x = x.values
        patterns = ['_'.join(np.diff((x + i)//8)[first:last].astype(str)) for i in range(8)]
        return pd.Series(patterns, index=np.arange(8))

    df = size_with_cp.apply(make_patterns, axis=1)

    B = df.values.flatten()
    total = pd.Series(B).groupby(B).size()

    if byte_pattern not in total.index:
        # assume maximum entropy
        return pd.Series(np.ones(len(words))/len(words), index=words.index)

    each = df.apply(lambda x: pd.Series(x).groupby(x).size(), axis=1).fillna(0)
    probs = each/total

    out = probs[byte_pattern]

    return out


def word_letter_sizes(words):
    rows = []
    for word in words:
        rows.append(np.array([char2huflen[c] for c in word]))

    df = pd.DataFrame(rows, index=words)

    return df


def prune_dictionary(keystrokes, words):
    # Guess the cp parameter
    keystrokes['cp'] = np.arange(len(keystrokes))+1

    # Successive frame length differences
    keystrokes['d'] = keystrokes['frame_length'].diff().fillna(-1).astype(int)

    # Size pattern for each token in the query
    s = keystrokes.groupby('token')['d'].apply(lambda x: tuple(x.astype(str))).tolist()

    # Strip the trailing spaces
    s = [si[:-1] for si in s[:-1]] + [s[-1]]

    # Starting cp for each token in the query
    cp = keystrokes.groupby('token')['cp'].apply(lambda x: x.iloc[0]).tolist()

    # Compressed size of each letter for each word in the dictionary
    base_sizes = {i:word_letter_sizes(words[i]) for i in words.keys()}

    # Prob of each word, given observed frame length differences
    word_probs = [incremental_compression(base_sizes[len(si)], si, cpi) for si,cpi in zip(s,cp)]

    # Keep only words with non-zero prob
    pruned_words = [p[p>0] for p in word_probs]

    # Only need the index
    pruned_words = [p.index.tolist() for p in pruned_words]

    return pruned_words
