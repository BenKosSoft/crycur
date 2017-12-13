"""
    Created by mbenlioglu & mertkosan on 12/13/2017
"""
from random import randint, choice
import string
import hashlib
import DSA
import sys

if sys.version_info < (3, 6):
    import sha3


def create_random_string(n):
    return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(n))


def GenSingleTx(p, q, g, alpha, beta):
    _LOWER = 1 << 127
    _UPPER = (1 << 128) - 1
    _SATOSHI_LOWER = 10
    _SATOSHI_UPPER = 500

    meta = "*** Bitcoin transaction ***\n"
    serial_number = "Serial number: " + str(randint(_LOWER, _UPPER)) + "\n"
    payer = "Payer: " + create_random_string(10) + "\n"
    payee = "Payee: " + create_random_string(10) + "\n"
    amount = "Amount: " + str(randint(_SATOSHI_LOWER, _SATOSHI_UPPER)) + " Satoshi\n"
    p_transaction = "p: " + str(p) + "\n"
    q_transaction = "q: " + str(q) + "\n"
    g_transaction = "g: " + str(g) + "\n"
    public_key_beta = "Public Key (beta): " + str(beta) + "\n"

    transaction_without_sign = meta + serial_number + payer + payee + \
                               amount + p_transaction + q_transaction + \
                               g_transaction + public_key_beta

    h = hashlib.sha3_256(transaction_without_sign).hexdigest()
    r, s = DSA.SignGen(h, p, q, g, alpha, beta)

    sign_r = "Signature (r): " + str(r) + "\n"
    sign_s = "Signature (s): " + str(s) + "\n"

    transaction = transaction_without_sign + sign_r + sign_s
    with open("SingleTransaction.txt", "w") as _file:
        _file.write(transaction)

    return transaction
