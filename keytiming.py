import numpy as np
import pandas as pd

def keystroke_timing(keystrokes, words):
    # TODO: timing model coming soon

    word_probas = []
    for words_i in words:
        df = pd.Series(np.ones(len(words_i))/len(words_i), index=words_i)
        word_probas.append(df)

    return word_probas
