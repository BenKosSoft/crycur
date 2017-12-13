"""
    Created by mbenlioglu & mertkosan on 12/13/2017
"""
from random import randint
from pyprimes import isprime
import os


def DL_Param_Generator(small_bound, large_bound):
    # generate q
    small_lb, small_ub = 1 << (small_bound-1), (1 << small_bound) - 1
    while True:
        q = randint(small_lb, small_ub)
        is_prime = isprime(q)
        if is_prime:
            break

    # generate p
    lower_multiplier = ((1 << (large_bound-1)) + q - 1) / q
    upper_multiplier = ((1 << large_bound) - 1) / q
    while True:
        p = randint(lower_multiplier, upper_multiplier) * q + 1
        is_prime = isprime(p)
        if is_prime:
            break

    # generate g
    while True:
        alpha = randint(2, p - 1)
        g = pow(alpha, (p-1)/q, p)
        if 1 != g:
            break

    # Writing to file
    with open("DSA params.txt", 'w') as _file:
        _file.write(str(q) + "\n")
        _file.write(str(p) + "\n")
        _file.write(str(g))

    return q, p, g


def KeyGen(p, q, g):
    pass


def SignGen(m, p, q, g, alpha, beta):
    pass


def SignVer(m, r, s, p, q, g, beta):
    pass


def SignVerFromFile(filename):
    if os.path.exists(filename):
        with open(filename) as _file:
            transaction = _file.read()
            lines = transaction.split('\n')
            p = long(lines[5][3:])
            q = long(lines[6][3:])
            g = long(lines[7][3:])
            beta = long(lines[8][19:])
            r = long(lines[9][15:])
            s = long(lines[10][15:])
        if SignVer(transaction, r, s, p, q, g, beta):
            print "Signature is valid!"
        else:
            print "Signature is not valid!"
    else:
        print filename + " doesn't exist!"
