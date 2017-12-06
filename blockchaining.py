from random import randint, choice
import sys, string
import hashlib


def create_random_string(n):
    return ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(n))


_SATOSHI_LOWER = 10
_SATOSHI_UPPER = 500

_LOWER = 2 ** 127
_UPPER = 2 ** 128 - 1
_TRANSACTION_NUMBER = 10

if sys.version_info < (3, 6):
    import sha3

_file = open("LongestChain.txt", "w")

h = "First transaction"
for i in range(_TRANSACTION_NUMBER):
    meta = "*** Bitcoin transaction ***\n"
    serial_number = "Serial number: " + str(randint(_LOWER, _UPPER)) + "\n"
    payer = "Payer: " + "BENKOSSOFT\n"
    payee = "Payee: " + create_random_string(10) + "\n"
    amount = "Amount: " + str(randint(_SATOSHI_LOWER, _SATOSHI_UPPER)) + " Satoshi\n"
    previous_hash = "Previous hash in the chain: " + str(h) + "\n"
    nonce = "Nonce: " + str(randint(_LOWER, _UPPER)) + "\n"

    transaction_without_nonce = meta + serial_number + payer + payee + amount + previous_hash
    transaction_with_nonce = transaction_without_nonce + nonce
    h = hashlib.sha3_256(transaction_with_nonce).hexdigest()

    while h[0:6] != "000000":
        nonce = "Nonce: " + str(randint(_LOWER, _UPPER)) + "\n"
        transaction_with_nonce = transaction_without_nonce + nonce
        h = hashlib.sha3_256(transaction_with_nonce).hexdigest()

    _file.write(transaction_with_nonce)
    _file.write("Proof of Work: " + str(h) + "\n")

_file.close()
