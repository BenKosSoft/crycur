"""
    Created by mbenlioglu on 12/20/2017
"""
import os
import sys
import string
from random import randint, choice
import hashlib
if sys.version_info < (3, 6):
    import sha3


def _num_lines(path):
    i = -1
    with open(path) as f:
        for i, _ in enumerate(f):
            pass
    return i + 1


def _get_last_line(fpath):
    line = ''
    with open(fpath) as f:
        for l in f:
            pass


def _get_merkle_root_hash(blockpath, TxLen):
    transactions_hashes = []
    with open(blockpath) as _file:
        lines = _file.readlines()
        transaction_len = len(lines) / TxLen
        for i in range(transaction_len):
            transaction = "".join(lines[i*TxLen:i*TxLen+TxLen])
            transactions_hashes.append(hashlib.sha3_256(transaction).hexdigest())
    print transactions_hashes



def PoW(TxBlockFile, ChainFile, PoWLen, TxLen):
    if not os.path.exists(TxBlockFile) or not os.path.isfile(TxBlockFile):
        raise ValueError('TxBlockFile: given path does not exist or not a file')

    with open(TxBlockFile) as tbf:
        nonce_lb, nonce_ub = 1 << (128 - 1), (1 << 128) - 1
        if not os.path.exists(ChainFile) or not os.path.isfile(ChainFile):
            prev_pow = 'Day Zero Link in the Chain'
        else:
            prev_pow
