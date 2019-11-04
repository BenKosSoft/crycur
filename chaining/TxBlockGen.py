"""
    Created by mbenlioglu & mertkosan on 12/20/2017
"""
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
                                 transaction_constants['serial'] + str(randint(_SERIAL_NO_LOWER, _SERIAL_NO_UPPER)),
                                 transaction_constants['p'] + str(p),
                                 transaction_constants['q'] + str(q),
                                 transaction_constants['g'] + str(g),
                                 transaction_constants['payer_key'] + str(beta_payer),
                                 transaction_constants['payee_key'] + str(beta_payee),
                                 transaction_constants['amount'] + str(randint(_SATOSHI_LOWER, _SATOSHI_UPPER))
                                 + transaction_constants['unit'] + '\n'])
        r, s = DSA.sign_gen(signed_part, p, q, g, alpha_payer, beta_payer)
        transaction += signed_part + transaction_constants['sig_r'] + str(r) + "\n"
        transaction += transaction_constants['sig_s'] + str(s) + "\n"

    # write to file
    if filename is not None:
        with open(str(filename), "wb") as tbf:
            tbf.write(transaction.encode('utf-8'))
            tbf.flush()
    return transaction
