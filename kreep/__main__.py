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
import argparse
import pkg_resources

from kreep import kreep

MODELS_PATH = pkg_resources.resource_filename('kreep', 'models/')
DEFAULT_LANGUAGE = os.path.join(MODELS_PATH, 'language.arpa')
DEFAULT_BIGRAMS = os.path.join(MODELS_PATH, 'bigrams.csv')


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog='kreep', description='Keystroke recognition and entropy elimination program')
    parser.add_argument('pcap', type=str,
                        help='filename of the pcap')
    parser.add_argument('--language', type=str, default=DEFAULT_LANGUAGE,
                        help='filename of the language model (.arpa format)')
    parser.add_argument('--bigrams', type=str, default=DEFAULT_BIGRAMS,
                        help='filename of the keystroke timing model (.csv format)')
    parser.add_argument('--website', type=str, default=None,
                        help='name of the website. Currently supported are: google, baidu. If not specified, try to guess.')
    parser.add_argument('--k', type=int, default=50,
                        help='number of hypotheses to generate')
    parser.add_argument('--alpha', type=float, default=0.2,
                        help='weight of the language model')

    args = parser.parse_args(args)
    hypotheses = kreep(**vars(args))
    print('\n'.join(hypotheses))


if __name__ == "__main__":
    main()
