"""
    Created by mbenlioglu on 12/20/2017
"""
import os
import sys
from multiprocessing import Process, Queue
from collections import deque
from random import randint
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
        for line in f:
            pass
    return line


def _get_merkle_root_hash(blockpath, TxLen):
    transactions_hashes = []
    with open(blockpath) as _file:
        lines = _file.readlines()
        transaction_len = len(lines) / TxLen
        for i in xrange(transaction_len):
            transaction = "".join(lines[i*TxLen:i*TxLen+TxLen])
            transactions_hashes.append(hashlib.sha3_256(transaction).hexdigest())
    transactions_hashes = deque(transactions_hashes)
    _len = len(transactions_hashes)
    while _len > 1:
        a = transactions_hashes.popleft()
        b = transactions_hashes.popleft()
        val = hashlib.sha3_256(a + b).hexdigest()
        transactions_hashes.append(val)
        _len = len(transactions_hashes)
    return transactions_hashes.pop()


def _find_fitting_hash(multi_q, nonce_lb, nonce_ub, prev_pow, root_hash, PoWLen):
    try:
        while True:
            nonce = str(randint(nonce_lb, nonce_ub))
            cur_pow = hashlib.sha3_256('\n'.join((prev_pow, root_hash, nonce, ''))).hexdigest()
            if cur_pow[0:PoWLen] == '0' * PoWLen:
                multi_q.put((nonce, cur_pow))
                break
    except KeyboardInterrupt:
        multi_q.put((None, None))


def PoW(TxBlockFile, ChainFile, PoWLen, TxLen, num_processes=1):
    if not os.path.exists(TxBlockFile) or not os.path.isfile(TxBlockFile):
        raise ValueError('TxBlockFile: given path does not exist or not a file')

    nonce_lb, nonce_ub = 1 << (128 - 1), (1 << 128) - 1
    if not os.path.exists(ChainFile) or not os.path.isfile(ChainFile):
        prev_pow = 'Day Zero Link in the Chain'
    else:
        prev_pow = _get_last_line(ChainFile)[:-1]
    root_hash = _get_merkle_root_hash(TxBlockFile, TxLen)

    processes = []
    multi_q = Queue()
    for i in xrange(num_processes):
        processes.append(Process(target=_find_fitting_hash,
                                 args=(multi_q, nonce_lb, nonce_ub, prev_pow, root_hash, PoWLen)))
        processes[i].start()

    nonce, cur_pow = multi_q.get()
    # terminate processes and clear queue
    for p in processes:
        p.terminate()
    while not multi_q.empty():
        multi_q.get()
    with open(ChainFile, 'a+') as cf:
        cf.write('\n'.join((prev_pow, root_hash, nonce, cur_pow, '')))
        cf.flush()
