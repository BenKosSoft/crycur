"""
    Created by mbenlioglu & mertkosan on 12/13/2017
"""
from random import randint
from pyprimes import isprime, nprimes
import hashlib
import sys
import os
import warnings

if sys.version < (3, 6):
    import sha3

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
        quotient = r / newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        raise ValueError('number does not have a multiplicative inverse in given modulo')
    return t if t > 0 else t + modulo


def dl_param_generator(small_bound, large_bound, filepath=None):
    # generate q
    # small_bound, large_bound = len(bin(small_bound)) - 3, len(bin(large_bound)) - 3
    small_lb, small_ub = 1 << (small_bound - 1), (1 << small_bound) - 1
    while True:
        q = randint(small_lb, small_ub)
        if _first_prime_check(q):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                is_prime = isprime(q)
                if is_prime:
                    break

    # generate p
    lower_multiplier = ((1 << (large_bound - 1)) + q - 1) / q
    upper_multiplier = ((1 << large_bound) - 1) / q
    while True:
        p = randint(lower_multiplier, upper_multiplier) * q + 1
        if _first_prime_check(p):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                is_prime = isprime(p)
                if is_prime:
                    break

    # generate g
    while True:
        alpha = randint(2, p - 1)
        g = pow(alpha, (p - 1) / q, p)
        if 1 != g:
            break

    # Writing to file
    if filepath is not None:
        with open(str(filepath), 'wb') as _file:
            _file.write(str(q) + "\n")
            _file.write(str(p) + "\n")
            _file.write(str(g))

    return q, p, g


def key_gen(p, q, g, write_file=True):
    alpha = randint(1, q - 1)
    beta = pow(g, alpha, p)
    if write_file:
        with open('DSA_skey.txt', 'wb') as f:
            f.write('%(q)d\n%(p)d\n%(g)d\n%(alpha)d\n' % {'q': q, 'p': p, 'g': g, 'alpha': alpha})
        with open('DSA_pkey.txt', 'wb') as f:
            f.write('%(q)d\n%(p)d\n%(g)d\n%(beta)d\n' % {'q': q, 'p': p, 'g': g, 'beta': beta})
    return alpha, beta


def sign_gen(msg, p, q, g, alpha, beta):
    msg_hash = int(hashlib.sha3_256(msg).hexdigest(), 16) % q
    k = randint(1, q - 1)
    r = pow(g, k, p) % q
    s = (alpha * r + k * msg_hash) % q
    return r, s


def sign_ver(msg, r, s, p, q, g, beta):
    msg_hash = int(hashlib.sha3_256(msg).hexdigest(), 16) % q
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
            p = long(lines[5][3:])
            q = long(lines[6][3:])
            g = long(lines[7][3:])
            beta = long(lines[8][19:])
            r = long(lines[9][15:])
            s = long(lines[10][15:])
        if sign_ver(signed_part, r, s, p, q, g, beta):
            print "Signature is valid!"
        else:
            print "Signature is not valid!"
    else:
        print filename + " doesn't exist!"
