import os
import sys
import numpy as np
import pandas as pd

from util import load_pcap, load_words
from detection import detect_keystrokes
from tokenization import tokenize_words
from compression import prune_dictionary
from keytiming import keystroke_timing
from language import predict_phrases


def main(fname):
    # Load the pcap
    df = load_pcap(fname)

    # Load the dictionary
    words = load_words('dictionary.txt')

    # TODO: detect website, for now, let the user specify google/baidu

    # Detect keystrokes
    keystrokes = detect_keystrokes(df, 'google')

    # Detect space keys to create word tokens
    keystrokes['token'] = tokenize_words(keystrokes, 'google', max(words.keys()))

    # Prune the dictionary from compression info leakage
    pruned_words = prune_dictionary(keystrokes, words)

    print('Detected a query with token lengths:', end='')
    for p in pruned_words:
        print(' ', len(p[0]), end='')
    print()

    # TODO: timing and language model coming soon
    # Word probabilities from keystroke timing
    # word_probas = keystroke_timing(keystrokes, pruned_words)

    # Generate query hypotheses with a language model
    # phrases = predict_phrases(pruned_words, word_probas)

    # print(phrases)


if __name__ == '__main__':
    fname = sys.argv[1]

    main(fname)
