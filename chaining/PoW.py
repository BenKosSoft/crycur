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


def _get_last_line(path):
    line = ''
    with open(path) as f:
        for line in f:
            pass
    return line


def _get_merkle_root_hash(block_path, tx_len):
    transactions_hashes = []
    with open(block_path) as _file:
        lines = _file.readlines()
        transaction_len = len(lines) / tx_len
        for i in xrange(transaction_len):
            transaction = "".join(lines[i*tx_len:i*tx_len+tx_len])
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


def _find_fitting_hash(multi_q, nonce_lb, nonce_ub, prev_pow, root_hash, pow_len):
    try:
        while True:
            nonce = str(randint(nonce_lb, nonce_ub))
            cur_pow = hashlib.sha3_256('\n'.join((prev_pow, root_hash, nonce, ''))).hexdigest()
            if cur_pow[0:pow_len] == '0' * pow_len:
                multi_q.put((nonce, cur_pow))
                break
    except KeyboardInterrupt:
        multi_q.put((None, None))


def calculate_pow(tx_block_file, chain_file, pow_len, tx_len, num_processes=1):
    if not os.path.exists(tx_block_file) or not os.path.isfile(tx_block_file):
        raise ValueError('tx_block_file: given path does not exist or not a file')

    nonce_lb, nonce_ub = 1 << (128 - 1), (1 << 128) - 1
    if not os.path.exists(chain_file) or not os.path.isfile(chain_file):
        prev_pow = 'Day Zero Link in the Chain'
    else:
        prev_pow = _get_last_line(chain_file)[:-1]
    root_hash = _get_merkle_root_hash(tx_block_file, tx_len)

    processes = []
    multi_q = Queue()
    for i in xrange(num_processes):
        processes.append(Process(target=_find_fitting_hash,
                                 args=(multi_q, nonce_lb, nonce_ub, prev_pow, root_hash, pow_len)))
        processes[i].start()

    nonce, cur_pow = multi_q.get()
    # terminate processes and clear queue
    for p in processes:
        p.terminate()
    while not multi_q.empty():
        multi_q.get()
    with open(chain_file, 'a+') as cf:
        cf.write('\n'.join((prev_pow, root_hash, nonce, cur_pow, '')))
        cf.flush()
