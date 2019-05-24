from operator import itemgetter


def predict_phrases(word_probs, lm, k=50, alpha=0.2):
    T = len(word_probs)

    # List of (token, score)
    beam = [((),0)]

    for t in range(T):
        word_probs_i = word_probs[t]

        new_beam = []
        for l,l_score in beam:
            for token, km_prob in word_probs_i.iteritems():
                l_plus = l + (token,)

                lm_prob = lm(l_plus)
                # lm_prob = lm(l_plus) - lm(l)

                score = l_score + km_prob + lm_prob * alpha
                new_beam.append((l_plus,score))

        beam = sorted(new_beam, key=itemgetter(1), reverse=True)[:k]

    top_k = [' '.join(l) for l,score in beam]
    return top_k
