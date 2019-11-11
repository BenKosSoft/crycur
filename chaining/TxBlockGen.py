"""
    Created by mbenlioglu & mertkosan on 12/20/2017
"""
from __future__ import absolute_import

from signature import DSA
from random import randint

_SERIAL_NO_LOWER = 1 << 127
_SERIAL_NO_UPPER = (1 << 128) - 1

_SATOSHI_LOWER = 10
_SATOSHI_UPPER = 500

transaction_constants = {'title': '*** Bitcoin transaction ***',
                         'serial': 'Serial number: ',
                         'p': 'p: ',
                         'q': 'q: ',
                         'g': 'g: ',
                         'payer_key': 'Payer Public Key (beta): ',
                         'payee_key': 'Payee Public Key (beta): ',
                         'amount': 'Amount: ',
                         'unit': ' Satoshi',
                         'sig_r': 'Signature (r): ',
                         'sig_s': 'Signature (s): '}


def gen_tx_block(p, q, g, count, filename=None):
    transaction = ""
    for _ in range(count):
        alpha_payer, beta_payer = DSA.key_gen(p, q, g, write_file=False)
        alpha_payee, beta_payee = DSA.key_gen(p, q, g, write_file=False)
        signed_part = '\n'.join([transaction_constants['title'],
                                 transaction_constants['serial'] + format(randint(_SERIAL_NO_LOWER, _SERIAL_NO_UPPER), 'x'),
                                 transaction_constants['p'] + format(p, 'x'),
                                 transaction_constants['q'] + format(q, 'x'),
                                 transaction_constants['g'] + format(g, 'x'),
                                 transaction_constants['payer_key'] + format(beta_payer, 'x'),
                                 transaction_constants['payee_key'] + format(beta_payee, 'x'),
                                 transaction_constants['amount'] + str(randint(_SATOSHI_LOWER, _SATOSHI_UPPER))
                                 + transaction_constants['unit'] + '\n'])
        r, s = DSA.sign_gen(signed_part, p, q, g, alpha_payer, beta_payer)
        transaction += signed_part + transaction_constants['sig_r'] + format(r, 'x') + "\n"
        transaction += transaction_constants['sig_s'] + format(s, 'x') + "\n"

    # write to file
    if filename is not None:
        with open(str(filename), "wb") as tbf:
            tbf.write(transaction.encode('utf-8'))
            tbf.flush()
    return transaction
