import os
import sys
import numpy as np
import pandas as pd

from .util import load_pcap, load_words, load_language, load_bigrams
from .detection import detect_keystrokes
from .tokenization import tokenize_words
from .compression import prune_dictionary
from .keytiming import keystroke_timing
from .language import predict_phrases


def kreep(fname, dictionary_fname, language_fname, bigrams_fname):
    # Load the pcap
    df = load_pcap(fname)

    # Load the dictionary
    words = load_words(dictionary_fname)
    lm = load_language(language_fname)
    bigrams = load_bigrams(bigrams_fname)

    # TODO: detect website, for now, let the user specify google/baidu

    # Detect keystrokes
    keystrokes = detect_keystrokes(df, 'google')

    # Detect space keys to create word tokens
    keystrokes['token'] = tokenize_words(keystrokes, 'google', max(words.keys()))

    # Prune the dictionary from compression info leakage
    pruned_words = prune_dictionary(keystrokes, words)

    # TODO: timing and language model coming soon
    # Word probabilities from keystroke timing
    word_probas = keystroke_timing(bigrams, keystrokes, pruned_words)

    # Generate query hypotheses with a language model
    phrases = predict_phrases(word_probas, lm)

    return phrases


if __name__ == '__main__':
    fname = sys.argv[1]

    main(fname)
