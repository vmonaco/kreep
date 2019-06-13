#---------------------------------------------------------------
# kreep - keystroke recognition and entropy elimination program
#   by Vinnie Monaco
#   www.vmonaco.com
#   contact AT vmonaco DOT com
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

import os
import sys
import numpy as np
import pandas as pd

from .util import load_pcap, load_words, load_language, load_bigrams
from .detection import detect_website_keystrokes, detect_keystrokes
from .tokenization import tokenize_words
from .compression import prune_dictionary
from .keytiming import keystroke_timing
from .beam import predict_phrases


def kreep(pcap, language, bigrams, k, alpha, website=None):
    # Load the pcap
    pcap = load_pcap(pcap)

    # Load the dictionary, language, and timing models
    bigrams = load_bigrams(bigrams)
    language, words = load_language(language)

    if website is None:
        website, keystrokes = detect_website_keystrokes(pcap)
    else:
        keystrokes = detect_keystrokes(pcap, website)

    # Detect keystrokes
    keystrokes = detect_keystrokes(pcap, website)

    # Detect space keys to create word tokens
    keystrokes['token'] = tokenize_words(keystrokes, website, max(words.keys()))

    if website == 'google':
        # Prune the dictionary from compression info leakage
        word_lists = prune_dictionary(keystrokes, words)
    else:
        # No pruning
        word_lens = keystrokes.groupby('token').size()
        word_lens[:-1] -= 1  # trailing space for first n-1 words
        word_lists = [words[i] for i in word_lens]

    # Word probabilities from keystroke timing
    word_probas = keystroke_timing(bigrams, keystrokes, word_lists)

    # Generate query hypotheses with a language model
    phrases = predict_phrases(word_probas, language, k=k, alpha=alpha)

    return phrases
