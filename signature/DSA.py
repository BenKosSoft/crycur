"""
    Created by mbenlioglu & mertkosan on 12/13/2017
"""
from random import randint
from pyprimes import primes
import hashlib
import sys
if sys.version < (3, 6):
    import sha3


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


def DL_Param_Generator(small_bound, large_bound):
    pass


def KeyGen(p, q, g):
    alpha = randint(1, q - 1)
    beta = pow(g, alpha, p)
    with open('DSA_skey.txt', 'w') as f:
        f.write('%(q)d\n%(p)d\n%(g)d\n%(alpha)d\n'
                % {'q': q, 'p': p, 'g': g, 'alpha': alpha})
    with open('DSA_pkey.txt', 'w') as f:
        f.write('%(q)d\n%(p)d\n%(g)d\n%(beta)d\n'
                % {'q': q, 'p': p, 'g': g, 'beta': beta})
    return alpha, beta


def SignGen(msg, p, q, g, alpha, beta):
    msg_hash = int(hashlib.sha3_256(msg).hexdigest(), 16) % p
    k = randint(1, q - 1)
    r = pow(g, k, p)
    s = (alpha * r + k * msg_hash) % q
    return r, s


def SignVer(msg, r, s, p, q, g, beta):
    msg_hash = int(hashlib.sha3_256(msg).hexdigest(), 16) % p
    v = _multiplicative_inverse(msg_hash, q)
    z1 = (s * v) % q
    z2 = ((q - r) * v) % q
    u = (pow(g, z1, p) * pow(beta, z2, p)) % p
    return r == u
