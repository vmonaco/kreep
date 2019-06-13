#---------------------------------------------------------------
# kreep - keystroke recognition and entropy elimination program
#   by Vinnie Monaco
#   www.vmonaco.com
#   contact AT vmonaco DOT com
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

from operator import itemgetter


def predict_phrases(word_probs, lm, k, alpha):
    T = len(word_probs)

    # the beam is a list of tuples: [(tokens, score), ...]
    beam = [((),0)]

    for t in range(T):
        word_probs_i = word_probs[t]

        new_beam = []
        for l,l_score in beam:
            for token, km_prob in word_probs_i.iteritems():
                lm_prob = lm(token, history=l)
                score = l_score + km_prob + lm_prob * alpha
                new_beam.append((l + (token,), score))

        beam = sorted(new_beam, key=itemgetter(1), reverse=True)[:k]

    top_k = [' '.join(l) for l,score in beam]
    return top_k
