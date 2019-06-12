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


def kreep(pcap, words, language, bigrams):
    # Load the pcap
    pcap = load_pcap(pcap)

    # Load the dictionary, language, and timing models
    words = load_words(words)
    language = load_language(language)
    bigrams = load_bigrams(bigrams)

    # TODO: detect website, for now, let the user specify google/baidu

    # Detect keystrokes
    keystrokes = detect_keystrokes(pcap, 'google')

    # Detect space keys to create word tokens
    keystrokes['token'] = tokenize_words(keystrokes, 'google', max(words.keys()))

    # Prune the dictionary from compression info leakage
    pruned_words = prune_dictionary(keystrokes, words)

    # Word probabilities from keystroke timing
    word_probas = keystroke_timing(bigrams, keystrokes, pruned_words)

    # Generate query hypotheses with a language model
    phrases = predict_phrases(word_probas, language)

    return phrases
