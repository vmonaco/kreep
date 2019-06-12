import os
import sys
import argparse
import pkg_resources

from kreep import kreep

MODELS_PATH = pkg_resources.resource_filename('kreep', 'models/')
DEFAULT_DICTIONARY = os.path.join(MODELS_PATH, 'words.dic')
DEFAULT_LANGUAGE = os.path.join(MODELS_PATH, 'language.arpa')
DEFAULT_BIGRAMS = os.path.join(MODELS_PATH, 'bigrams.csv')


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog='kreep', description='Keystroke recognition and entropy elimination program')
    parser.add_argument('pcap', type=str,
                        help='filename of the pcap')
    parser.add_argument('--words', type=str, default=DEFAULT_DICTIONARY,
                        help='filename of the dictionary (.txt or .dic format)')
    parser.add_argument('--language', type=str, default=DEFAULT_LANGUAGE,
                        help='filename of the language model (.arpa format)')
    parser.add_argument('--bigrams', type=str, default=DEFAULT_BIGRAMS,
                        help='filename of the keystroke timing model (.csv format)')

    args = parser.parse_args(args)
    hypotheses = kreep(**vars(args))
    print('\n'.join(hypotheses))


if __name__ == "__main__":
    main()
