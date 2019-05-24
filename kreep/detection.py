import numpy as np
import pandas as pd
from scipy import stats
from itertools import product


def google_rule(a, e, ta, te):
    d = e - a[-1]

    if len(a) <= 2 and te - ta > 2000:
        return False

    # Only one decrease allowed
    if d < 0:
        pd = np.diff(a)
        return len(a) >= 5 and (pd < 0).sum() <= 0

    # No consecutive 0s
    if d == 0:
        return 0 not in np.diff(a[-2:])

    if d == 1:
        return True

    if d == 2:
        return True

    if d == 3:
        return True

    if d >= 4:
        pd = np.diff(a)
        return len(a) >= 5 and (pd >= 4).sum() <= 2

    return False


def baidu_rule(a, e, ta, te):
    d = e - a[-1]

    if len(a) <= 2 and te - ta > 2000:
        return False

    if d >= 2 and d <= 30:
        return True

    return False


def yandex_rule(a, e, ta, te):
    d = e - a[-1]

    if len(a) <= 2 and te - ta > 2000:
        return False

    if d == 1:
        return True

    if d == 2:
        return True

    if d == 3:
        return True

    if d == 4:
        return True

    return False


def longest_dfa_sequence(a, t, append_rule):
    '''
    Find the longest subsequence accepted by a DFA. append_rule returns True or
    False to indicate whether the DFA that accepted sequence a can transition
    after appending element t
    '''
    n = len(a)
    L = [[] for _ in range(n)]
    idx = [[] for _ in range(n)]

    L[0].append(a[0])
    idx[0].append(0)

    for i in range(1, n):
        for j in range(i):
            if append_rule(L[j], a[i], t[j], t[i]) and len(L[i]) < len(L[j]) + 1:
                L[i] = L[j].copy()
                idx[i] = idx[j].copy()

        L[i].append(a[i])
        idx[i].append(i)

    m = idx[0]

    for x in idx:
        if len(x) > len(m):
            m = x;

    return m


def detect_keystrokes(df, website):
    append_rules = {
        'google':google_rule,
        'baidu':baidu_rule,
        'yandex':yandex_rule
    }

    # At least the min size of a GET request
    df = df[df['frame_length']>100]

    result = []
    for dst, protocol in df[['dst','protocol']].drop_duplicates().values:
        df_dst = df[(df['dst']==dst)&(df['protocol']==protocol)]
        idx = longest_dfa_sequence(df_dst['frame_length'].values.tolist(), df_dst['frame_time'].values.tolist(),
                                append_rule=append_rules[website])

        if len(idx) > len(result):
            result = df_dst.iloc[idx]

    return result
