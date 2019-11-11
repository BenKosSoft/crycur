"""
    Created by mbenlioglu & mertkosan on 12/13/2017
"""
from __future__ import absolute_import, print_function, division

from random import randint
from pyprimes import is_prime, nprimes
from multiprocessing import Process, Queue
import hashlib
import sys
import os
import warnings

if sys.version_info < (3, 6):
    import sha3

# Python 2.7 compatibility
try:
    range = xrange
except NameError:
    pass

prime_list = list(nprimes(30))


def _first_prime_check(p):
    for prime in prime_list:
        if p % prime == 0:
            return False
    return True


def _multiplicative_inverse(num, modulo):
    """
    Return the multiplicative inverse of the given number in given modulo or raises a ValueError if no inverse exists.
    :param num: Number to be inverted
    :type num: int
    :param modulo:
    :type modulo: int
    :raises ValueError if num has no inverse
    :return: multiplicative inverse of the number in the given modulo
    """
    t = 0
    r = modulo
    newt = 1
    newr = num

    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        raise ValueError('number does not have a multiplicative inverse in given modulo')
    return t if t > 0 else t + modulo


def _terminate_clear(processes, multi_q):
    for pr in processes:
        pr.terminate()
    while not multi_q.empty():
        multi_q.get()


def _generate_prime(multi_q, lower_bound, upper_bound, mult=1, shift=0):
    try:
        while True:
            q = randint(lower_bound, upper_bound) * mult + shift
            if _first_prime_check(q):
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    if is_prime(q):
                        multi_q.put(q)
                        break
    except KeyboardInterrupt:
        multi_q.put(None)


def _generate_generator(multi_q, p, q):
    try:
        while True:
            alpha = randint(2, p - 1)
            g = pow(alpha, (p - 1) // q, p)
            if 1 != g:
                multi_q.put(g)
                break
    except KeyboardInterrupt:
        multi_q.put(None)


def dl_param_generator(small_bound, large_bound, num_processes=1, filepath=None):
    # generate q
    # small_bound, large_bound = len(bin(small_bound)) - 3, len(bin(large_bound)) - 3
    small_lb, small_ub = 1 << (small_bound - 1), (1 << small_bound) - 1

    processes = []
    multi_q = Queue()
    for i in range(num_processes):
        processes.append(Process(target=_generate_prime, args=(multi_q, small_lb, small_ub)))
        processes[i].start()
    q = multi_q.get()

    # terminate processes and clear queue
    _terminate_clear(processes, multi_q)

    # generate p
    multi_q = Queue()
    lower_multiplier = ((1 << (large_bound - 1)) + q - 1) // q
    upper_multiplier = ((1 << large_bound) - 1) // q
    for i in range(num_processes):
        processes[i] = Process(target=_generate_prime, args=(multi_q, lower_multiplier, upper_multiplier, q, 1))
        processes[i].start()
    p = multi_q.get()

    # terminate processes and clear queue
    _terminate_clear(processes, multi_q)

    # generate g
    multi_q = Queue()
    for i in range(num_processes):
        processes[i] = Process(target=_generate_generator, args=(multi_q, p, q))
        processes[i].start()
    g = multi_q.get()

    # terminate processes and clear queue
    _terminate_clear(processes, multi_q)

    # Writing to file
    if filepath is not None:
        with open(str(filepath), 'wb') as _file:
            _file.write((format(q, 'x') + "\n").encode('utf-8'))
            _file.write((format(p, 'x') + "\n").encode('utf-8'))
            _file.write(format(g, 'x').encode('utf-8'))

    return q, p, g


def key_gen(p, q, g, write_file=True):
    alpha = randint(1, q - 1)
    beta = pow(g, alpha, p)
    if write_file:
        with open('DSA_skey.txt', 'wb') as f:
            f.write(('%(q)x\n%(p)x\n%(g)x\n%(alpha)x\n' % {'q': q, 'p': p, 'g': g, 'alpha': alpha}).encode('utf-8'))
        with open('DSA_pkey.txt', 'wb') as f:
            f.write(('%(q)x\n%(p)x\n%(g)x\n%(beta)x\n' % {'q': q, 'p': p, 'g': g, 'beta': beta}).encode('utf-8'))
    return alpha, beta


def sign_gen(msg, p, q, g, alpha, beta):
    msg_hash = int(hashlib.sha3_256(msg.encode('utf-8')).hexdigest(), 16) % q
    k = randint(1, q - 1)
    r = pow(g, k, p) % q
    s = (alpha * r + k * msg_hash) % q
    return r, s


def sign_ver(msg, r, s, p, q, g, beta):
    msg_hash = int(hashlib.sha3_256(msg.encode('utf-8')).hexdigest(), 16) % q
    v = _multiplicative_inverse(msg_hash, q)
    z1 = (s * v) % q
    z2 = ((q - r) * v) % q
    u = (pow(g, z1, p) * pow(beta, z2, p)) % p
    u = u % q
    return r == u


def sign_ver_from_file(filename):
    if os.path.exists(filename):
        with open(filename) as _file:
            lines = _file.readlines()
            signed_part = "".join(lines[0:len(lines) - 2])
            p = int(lines[5][3:], 16)
            q = int(lines[6][3:], 16)
            g = int(lines[7][3:], 16)
            beta = int(lines[8][19:], 16)
            r = int(lines[9][15:], 16)
            s = int(lines[10][15:], 16)
        if sign_ver(signed_part, r, s, p, q, g, beta):
            print("Signature is valid!")
        else:
            print("Signature is not valid!")
    else:
        print(filename + " doesn't exist!")
