"""
    Created by mbenlioglu on 12/21/2017
"""
import os
import sys
import PoW
import TxBlockGen

blockCount = 2001  # number of link in the block chain (you can change)
TxCount = 8  # number of transactions in a block (you can change, but set it to a power of two)
PoWLen = 6  # the number of 0s in PoW (you can change)
TxLen = 10  # no of lines in a transaction (do not change)
LinkLen = 4  # no of lines in a link of the chain (do not change)

log_file = '.log'
block_dir = 'blocks/'
block_prefix = 'TransactionBlock'
block_filename_template = block_prefix + '%d.txt'
dsa_param_file = 'DSA_params.txt'
chain_file_name = "LongestChain.txt"


def create_blocks(start=0):
    print '=' * 100
    print 'Starting creating blocks'
    print '=' * 100
    if os.path.exists(dsa_param_file):
        inf = open(dsa_param_file, 'r')
        q = int(inf.readline())
        p = int(inf.readline())
        g = int(inf.readline())
        inf.close()
        print "DSA parameters are read from file", dsa_param_file
    else:
        print dsa_param_file, 'does not exist'
        sys.exit()

    file_name = os.path.join('.', block_dir, block_filename_template)
    try:
        os.makedirs(os.path.dirname(file_name))
    except OSError:
        pass

    for j in range(start, blockCount):
        transaction = TxBlockGen.GenTxBlock(p, q, g, TxCount)
        tx_block_file_name = file_name % j
        with open(tx_block_file_name, "w") as tbf:
            tbf.write(transaction)
            tbf.flush()
        print "Transaction block %d is written into TransactionBlock%d.txt" % (j, j)


def mine():
    print '=' * 100
    print 'Starting mining'
    print '=' * 100
    is_block_calculated = False
    i = 0
    try:
        start = 0
        if os.path.exists(log_file) and os.path.isfile(log_file):
            with open(log_file) as log:
                start = int(log.read())
        print 'Starting from', start
        file_name = os.path.join('.', block_dir, block_filename_template)
        for i in range(start, blockCount):
            is_block_calculated = False
            tx_block_file_name = file_name % i
            if os.path.exists(tx_block_file_name):
                PoW.PoW(tx_block_file_name, chain_file_name, PoWLen, TxLen)
                is_block_calculated = True
                print "#%d Proof of work is written/appended to" % i, chain_file_name
            else:
                print "Error: ", tx_block_file_name, "does not exist. Logging and exiting..."
                with open(log_file, 'w') as log:
                    if not is_block_calculated:
                        log.write(str(i))
                        log.flush()
                    else:
                        log.write(str(i + 1))
                        log.flush()
                        sys.exit()
    except KeyboardInterrupt:
        sys.stdout.write('Keyboard Interrupt. Logging...')
        with open(log_file, 'w') as log:
            if not is_block_calculated:
                log.write(str(i))
                log.flush()
            else:
                log.write(str(i + 1))
                log.flush()
        sys.stdout.write(' done\n')


if __name__ == '__main__':
    should_create = True

    relative_block_dir = os.path.join('.', block_dir)
    existing_block_cnt = 0
    if os.path.exists(relative_block_dir) and os.path.isdir(relative_block_dir):
        existing_block_cnt = sum(1 for f in os.listdir(relative_block_dir)
                                 if os.path.isfile(os.path.join(relative_block_dir, f)) and f.startswith(block_prefix))
        if blockCount <= existing_block_cnt:
            should_create = False
    if should_create:
        create_blocks(existing_block_cnt)

    mine()
