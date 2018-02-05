"""
    Created by mbenlioglu & mertkosan on 12/21/2017
"""
import os
import errno
import sys
import argparse
import ConfigParser
from itertools import izip, repeat
from multiprocessing import freeze_support, cpu_count, Pool

from chaining import PoW, TxBlockGen
from signature import DSA

block_count = 200  # number of link in the block chain (you can change)
tx_count = 8  # number of transactions in a block (you can change, but set it to a power of two)
pow_len = 6  # the number of leading 0s in proof of work (you can change)
tx_len = 10  # no of lines in a transaction (do not change)
link_len = 4  # no of lines in a link of the chain (do not change)

log_file = '.crylog'  # not change
block_dir = './blocks/'
block_prefix = 'TransactionBlock'
block_filename_template = block_prefix + '-%d.block'
dsa_param_file = 'DSA_params.txt'
chain_file_name = "LongestChain.txt"
num_processes = 4


def _gen_tx_block_zipped(args):
    return TxBlockGen.gen_tx_block(*args)


def create_blocks(start=0):
    print '=' * 100
    print 'Starting creating blocks'
    print '=' * 100
    if os.path.exists(dsa_param_file):
        with open(dsa_param_file, 'r') as inf:
            q = int(inf.readline())
            p = int(inf.readline())
            g = int(inf.readline())
        print "DSA parameters are read from file", dsa_param_file
    else:
        sys.stdout.write('DSA parameter file not found! Generating....')
        sys.stdout.flush()
        DSA.dl_param_generator(256, 2048, True)
        sys.stdout.write(' done\n')
        return create_blocks(start)

    file_name = os.path.join(block_dir, block_filename_template)
    try:
        os.makedirs(os.path.dirname(file_name))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    sys.stdout.write('Generating %d missing transaction blocks...' % (block_count - start))
    sys.stdout.flush()
    pool = Pool(processes=num_processes)
    pool.imap_unordered(_gen_tx_block_zipped, izip(repeat(p), repeat(q), repeat(g), repeat(tx_count),
                                                   [file_name % j for j in xrange(start, block_count)]),
                        chunksize=50)
    pool.close()
    pool.join()
    sys.stdout.write(' done\n')


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
        file_name = os.path.join(block_dir, block_filename_template)
        for i in range(start, block_count):
            is_block_calculated = False
            tx_block_file_name = file_name % i
            if os.path.exists(tx_block_file_name):
                PoW.calculate_pow(tx_block_file_name, chain_file_name, pow_len, tx_len, num_processes=num_processes)
                is_block_calculated = True
                print "#%d Proof of work is written/appended to" % i, chain_file_name
            else:
                print "Error: ", tx_block_file_name, "does not exist. Logging and exiting..."
                with open(log_file, 'wb') as log:
                    if not is_block_calculated:
                        log.write(str(i))
                        log.flush()
                    else:
                        log.write(str(i + 1))
                        log.flush()
                        sys.exit()
    except KeyboardInterrupt:
        sys.stdout.write('Keyboard Interrupt. Logging...')
        sys.stdout.flush()
        with open(log_file, 'wb') as log:
            if not is_block_calculated:
                log.write(str(i))
                log.flush()
            else:
                log.write(str(i + 1))
                log.flush()
        sys.stdout.write(' done\n')


if __name__ == '__main__':
    freeze_support()
    should_create = True

    existing_block_cnt = 0
    if os.path.exists(block_dir) and os.path.isdir(block_dir):
        existing_block_cnt = sum(1 for f in os.listdir(block_dir)
                                 if os.path.isfile(os.path.join(block_dir, f)) and f.startswith(block_prefix))
        if block_count <= existing_block_cnt:
            should_create = False
    if should_create:
        create_blocks(existing_block_cnt)

    # mine()
