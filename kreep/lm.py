#---------------------------------------------------------------
# PyNLPl - Language Models
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import math
import sys

if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout


class ARPALanguageModel(object):

    """Full back-off language model, loaded from file in ARPA format.

    This class does not build the model but allows you to use a pre-computed one.
    You can use the tool ngram-count from for instance SRILM to actually build the model.

    """

    class NgramsProbs(object):
        """Store Ngrams with their probabilities and backoffs.

        This class is used in order to abstract the physical storage layout,
        and enable memory/speed tradeoffs.

        """

        def __init__(self, data, mode='simple', delim=' '):
            """Create an ngrams storage with the given method:

            'simple' method is a Python dictionary (quick, takes much memory).
            'trie' method is more space-efficient (~35% reduction) but slower.
            data is a dictionary of ngram-tuple => (probability, backoff).
            delim is the strings which converts ngrams between tuple and
            unicode string (for saving in trie mode).

            """
            self.delim = delim
            self.mode = mode
            if mode == 'simple':
                self._data = data
            elif mode == 'trie':
                import marisa_trie
                self._data = marisa_trie.RecordTrie("@dd", [(self.delim.join(k), v) for k, v in data.items()])
            else:
                raise ValueError("mode {} is not supported for NgramsProbs".format(mode))

        def prob(self, ngram):
            """Return probability of given ngram tuple"""
            return self._data[ngram][0] if self.mode == 'simple' else self._data[self.delim.join(ngram)][0][0]

        def backoff(self, ngram):
            """Return backoff value of a given ngram tuple"""
            return self._data[ngram][1] if self.mode == 'simple' else self._data[self.delim.join(ngram)][0][1]

        def __len__(self):
            return len(self._data)


    def __init__(self, filename, encoding='utf-8', encoder=None, base_e=True, dounknown=True, debug=False, mode='simple'):
        # parameters
        self.encoder = (lambda x: x) if encoder is None else encoder
        self.base_e = base_e
        self.dounknown = dounknown
        self.debug = debug
        self.mode = mode
        # other attributes
        self.total = {}

        data = {}

        with io.open(filename, 'rt', encoding=encoding) as f:
            order = None
            for line in f:
                line = line.strip()
                if line == '\\data\\':
                    order = 0
                elif line == '\\end\\':
                    break
                elif line.startswith('\\') and line.endswith(':'):
                    for i in range(1, 10):
                        if line == '\\{}-grams:'.format(i):
                            order = i
                            break
                    else:
                        raise ValueError("Order of n-gram is not supported!")
                elif line:
                    if order == 0:  # still in \data\ section
                        if line.startswith('ngram'):
                            n = int(line[6])
                            v = int(line[8:])
                            self.total[n] = v
                    elif order > 0:
                        fields = line.split('\t')
                        logprob = float(fields[0])
                        if base_e:  # * log(10) does log10 to log_e conversion
                            logprob *= math.log(10)
                        ngram = self.encoder(tuple(fields[1].split()))
                        if len(fields) > 2:
                            backoffprob = float(fields[2])
                            if base_e:  # * log(10) does log10 to log_e conversion
                                backoffprob *= math.log(10)
                            if self.debug:
                                msg = "Adding to LM: {}\t{}\t{}"
                                print(msg.format(ngram, logprob, backoffprob), file=stderr)
                        else:
                            backoffprob = 0.0
                            if self.debug:
                                msg = "Adding to LM: {}\t{}"
                                print(msg.format(ngram, logprob), file=stderr)
                        data[ngram] = (logprob, backoffprob)
                    elif self.debug:
                        print("Unable to parse ARPA LM line: " + line, file=stderr)
        self.order = order
        self.ngrams = self.NgramsProbs(data, mode)

    def score(self, data, history=None):
        result = 0
        for word in data:
            result += self.scoreword(word, history)
            if history:
                history += (word,)
            else:
                history = (word,)
        return result

    def scoreword(self, word, history=None):
        if isinstance(word, str) or (sys.version < '3' and isinstance(word, unicode)):
            word = (word,)

        if history:
            lookup = history + word
        else:
            lookup = word

        if len(lookup) > self.order:
            lookup = lookup[-self.order:]

        try:
            return self.ngrams.prob(lookup)
        except KeyError:  # not found, back off
            if not history:
                if self.dounknown:
                    try:
                        return self.ngrams.prob(('<unk>',))
                    except KeyError:
                        msg = "Word {} not found. And no history specified and model has no <unk>."
                        raise KeyError(msg.format(word))
                else:
                    msg = "Word {} not found. And no history specified."
                    raise KeyError(msg.format(word))
            else:
                try:
                    backoffweight = self.ngrams.backoff(history)
                except KeyError:
                    backoffweight = 0  # backoff weight will be 0 if not found
                return backoffweight + self.scoreword(word, history[1:])

    def __len__(self):
        return len(self.ngrams)
