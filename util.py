import dpkt
import socket
import string
import numpy as np
import pandas as pd

KEY_SET = list(string.ascii_lowercase)
INT2KEY = dict(enumerate(sorted(KEY_SET)))
KEY2INT = {v:k for k, v in INT2KEY.items()}


def ip_to_str(address):
    '''
    transform a int ip address to a human readable ip address (ipv4)
    '''
    return socket.inet_ntoa(address)


def load_pcap(fname):
    '''
    Load a pcap (ng) into a pandas DataFrame
    '''
    rows = []
    for ts, buf in dpkt.pcapng.Reader(open(fname,'rb')):
        eth = dpkt.ethernet.Ethernet(buf)
        if eth.type == dpkt.ethernet.ETH_TYPE_IP:
            ip = eth.data
            if ip.p == dpkt.ip.IP_PROTO_TCP:
                tcp = ip.data
                rows.append((ip_to_str(ip.src), ip_to_str(ip.dst), ts, len(tcp.data), ip.p))

    df = pd.DataFrame(rows, columns=['src','dst','frame_time','frame_length','protocol'])
    return df


def word2idx(word):
    return [KEY2INT[c] for c in word]


def idx2word(idx):
    return ''.join([INT2KEY[c] for c in idx])


def load_words(fname):
    words = pd.read_csv(fname, header=None).squeeze()

    words = words.dropna()
    words = words.str.lower()
    words = words.drop_duplicates()
    words = words.reset_index(drop=True)

    s = words.str.len()
    words_dict = {}
    for word_len in range(s.min(), s.max()+1):
        idx = words[s==word_len].apply(lambda x: np.array(word2idx(x))).values
        if len(idx) == 0:
            continue
        words_dict[word_len] = words[s==word_len].values

    return words_dict


def load_language(fname):
    import kenlm
    lm = kenlm.Model(fname)

    def lm_fun(s, lm=lm):
        marg = lm.score(' '.join(s), bos=False, eos=False)

        if len(s) > 1:
            prev = lm.score(' '.join(s[:-1]), bos=False, eos=False)
            return marg - prev
        else:
            return marg

    return lm_fun
