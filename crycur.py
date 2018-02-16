"""
    Created by mbenlioglu & mertkosan on 12/21/2017
"""
import os
import errno
import sys
import argparse
import ConfigParser
import hashlib
from itertools import izip, repeat, islice, cycle
from multiprocessing import freeze_support, cpu_count, Pool

from chaining import PoW, TxBlockGen
from signature import DSA
from strings import descriptions

if sys.version_info < (3, 6):
    import sha3


# ======================================================================================================================
# cmd callable functions and their helper functions
# ======================================================================================================================
def configure():
    if not configs.has_section('USER'):
        configs.add_section('USER')
    if cmd_args.set is not None:
        for param in cmd_args.set:
            configs.set('USER', param[0], param[1])
        with open('./config.ini', 'wb') as cfgfile:
            configs.write(cfgfile)
    elif cmd_args.get is not None:
        msg = '%s: %r'
        for param in cmd_args.get:
            try:
                val = configs.get('USER', param)
            except ConfigParser.NoOptionError:
                val = 'Option is not set!'
            print msg % (param, val)
    elif cmd_args.reset is not None:
        configs.remove_section('USER')
        configs.add_section('USER')
        with open('./config.ini', 'wb') as cfgfile:
            configs.write(cfgfile)


def _gen_tx_block_zipped(args):
    return TxBlockGen.gen_tx_block(*args)


def generate(gen_blocks=False, start=None, count=None, fill_gaps=None, gen_dsa=False, nobanner=False):
    # Generate DSA file
    if (hasattr(cmd_args, 'd') and cmd_args.d) or gen_dsa:
        sys.stdout.write('Generating DSA parameter file....')
        try:
            os.makedirs(os.path.dirname(dsa_param_file))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        sys.stdout.flush()
        DSA.dl_param_generator(256, 2048, num_processes, dsa_param_file)
        sys.stdout.write(' done\n')

    # Generate Transaction blocks
    if (hasattr(cmd_args, 'b') and cmd_args.b) or gen_blocks:
        if count is None:
            count = cmd_args.count if hasattr(cmd_args, 'count') and cmd_args.count is not None else chunk_size

        try:
            os.makedirs(blocks_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Adjust transaction numbers to be generated
        if (hasattr(cmd_args, 'fill_gaps') and cmd_args.fill_gaps) or fill_gaps:
            existing = sorted([int(os.path.splitext(f)[0][len(block_prefix) + 1:]) for f in os.listdir(blocks_dir)
                               if os.path.isfile(os.path.join(blocks_dir, f)) and f.startswith(block_prefix)])
            to_be_generated = []
            j = 0
            for e in existing:
                while j != e:
                    to_be_generated.append(j)
                    j = j + 1
                j = j + 1
        else:
            if start is None and cmd_args.ignore_existing:
                start = 0
            elif start is None:
                block_files = [int(os.path.splitext(f)[0][len(block_prefix):]) for f in os.listdir(blocks_dir)
                               if os.path.isfile(os.path.join(blocks_dir, f)) and f.startswith(block_prefix)]
                start = 0 if not block_files else max(block_files) + 1
            to_be_generated = xrange(start, start + count)

        if not nobanner:
            print '=' * 70
            print 'Starting creating blocks'
            print '=' * 70

        # Create blocks
        if os.path.exists(dsa_param_file):
            with open(dsa_param_file, 'r') as inf:
                q = int(inf.readline())
                p = int(inf.readline())
                g = int(inf.readline())
            print "DSA parameters are read from file", dsa_param_file
        else:
            print 'DSA parameters file could not be found!'
            return generate(gen_blocks, start, count, fill_gaps, True, nobanner)

        file_name = os.path.join(blocks_dir, block_filename_template)

        sys.stdout.write('Generating %d missing transaction blocks...' % len(to_be_generated))
        sys.stdout.flush()
        pool = Pool(processes=num_processes)
        pool.imap_unordered(_gen_tx_block_zipped, izip(repeat(p), repeat(q), repeat(g), repeat(tx_count),
                                                       [file_name % j for j in to_be_generated]),
                            chunksize=10)
        pool.close()
        pool.join()
        sys.stdout.write(' done\n')


def _log_last_block(block_no):
    with open(log_file, 'wb') as log:
        log.write(str(block_no) + '\n')
        log.flush()


def mine():
    print '=' * 70
    print 'Starting mining... Press Ctrl+C to pause'
    print '=' * 70
    if not cmd_args.no_generate:
        print 'Filling transaction block gaps...'
        generate(gen_blocks=True, fill_gaps=True, nobanner=True)
    i = 0
    try:
        if cmd_args.start_from is not None:
            i = int(cmd_args.start_from)
        elif os.path.exists(log_file) and os.path.isfile(log_file):
            print "Continuing from where it's left off..."
            with open(log_file) as log:
                i = int(log.read())
        print 'Starting from', i
        file_name = os.path.join(blocks_dir, block_filename_template)
        limit = i + mine_count
        while i < limit:
            tx_block_file_name = file_name % i
            if os.path.exists(tx_block_file_name):
                PoW.calculate_pow(tx_block_file_name, chain_file_name, pow_len, tx_len, num_processes=num_processes)
                print "#%d Proof of work is written/appended to" % i, chain_file_name
                i = i + 1
            elif not cmd_args.no_generate:
                generate(gen_blocks=True, start=i, count=chunk_size, nobanner=True)
            else:
                print "Error: ", tx_block_file_name, "does not exist. Logging and exiting..."
                _log_last_block(i)
                sys.exit()
        _log_last_block(i)
        print 'Done.'
    except KeyboardInterrupt:
        sys.stdout.write('Keyboard Interrupt. Logging...')
        sys.stdout.flush()
        _log_last_block(i)
        sys.stdout.write(' done\n')


def _validate_tx(args):
    block_no, tx_no, configs = args

    tx_len = configs.getint('DEFAULT', 'tx_len')
    link_len = configs.getint('DEFAULT', 'link_len')
    chain_file_name = configs.get('USER', 'chain_file')
    blocks_dir = configs.get('USER', 'blocks_dir')
    block_prefix = configs.get('USER', 'block_prefix')
    block_filename_template = block_prefix + '-%d.block'

    result = [0, block_no, tx_no]
    block_file_path = os.path.join(blocks_dir, block_filename_template % block_no)
    with open(block_file_path) as bfile:
        transaction = [l for l in islice(bfile, tx_no * tx_len, (tx_no + 1) * tx_len)]
        signed_part = "".join(transaction[0:tx_len - 2])
        p = int(transaction[2][len(TxBlockGen.transaction_constants['p']):])
        q = int(transaction[3][len(TxBlockGen.transaction_constants['q']):])
        g = int(transaction[4][len(TxBlockGen.transaction_constants['g']):])
        beta = int(transaction[5][len(TxBlockGen.transaction_constants['payer_key']):])
        r = int(transaction[8][len(TxBlockGen.transaction_constants['sig_r']):])
        s = int(transaction[9][len(TxBlockGen.transaction_constants['sig_s']):])
        if not DSA.sign_ver(signed_part, r, s, p, q, g, beta):
            result = [1, block_no, tx_no]
    with open(chain_file_name) as cfile:
        for i, line in enumerate(cfile):
            if i == link_len * block_no + 1:
                if line[:-1] != PoW.get_merkle_root_hash(block_file_path, tx_len):
                    result = [2, block_no, tx_count]
                    break
    return result


def validate():
    print '=' * 70
    print 'Starting validation...'
    print '=' * 70
    if cmd_args.chain:
        with open(chain_file_name) as chfile:
            sys.stdout.write('Checking block chain file... ')
            sys.stdout.flush()
            is_valid = True
            link = [None] * (link_len + 1)
            for i, line in enumerate(chfile):
                if i != 0 and i % link_len == 0:
                    if link[-1][0:pow_len] != '0' * pow_len:
                        sys.stdout.write('Invalid proof of work. Wrong number of leading zeros:\n' + link[-1])
                        is_valid = False
                        break
                    if link[-1][:-1] != hashlib.sha3_256(''.join(link[1:link_len])).hexdigest():
                        sys.stdout.write('Block chain does not validate! Broken link:\n', ''.join(link[1:]))
                        is_valid = False
                        break
                    if link[0] is not None and link[0] != link[1]:
                        sys.stdout.write('Previous hash not same in the next link! Prev hash:\n', link[0],
                                         '\nNext link:' + ''.join(link[1:]))
                        is_valid = False
                        break
                    link[0] = link[-1]
                link[(i % link_len) + 1] = line
            if is_valid:
                sys.stdout.write('OK...\n')
    if cmd_args.transactions:
        sys.stdout.write('Checking individual transactions... ')
        is_valid = True
        with open(chain_file_name, 'r') as cfile:
            block_count = sum(1 for _ in cfile) / link_len
        pool = Pool(processes=num_processes)
        for res in pool.imap_unordered(_validate_tx, izip(xrange(block_count), cycle(xrange(tx_count)), repeat(configs)),
                                       chunksize=10):
            if res[0] == 1:
                sys.stdout.write('Signature of the transaction does not verify. Block No:' + res[1] +
                                 'Tx No:' + res[2] + '\n')
                is_valid = False
            elif res[0] == 2:
                sys.stdout.write('Transaction does not belong to the block number. Block No:' + res[1] +
                                 'Tx No:' + res[2] + '\n')
                is_valid = False
        pool.close()
        pool.join()
        if is_valid:
            sys.stdout.write('OK...\n')


# ======================================================================================================================
# Type checking functions
# ======================================================================================================================
def _valid_dir(path):
    if not os.path.exists(path) or not os.path.isdir(path):
        msg = '%r is not a valid directory!' % path
        raise argparse.ArgumentTypeError(msg)
    return path


def _valid_file(path):
    if not os.path.exists(path) or not os.path.isfile(path):
        raise argparse.ArgumentTypeError('%r is not a valid file!' % path)
    return path


def _positive_int(val):
    ival = int(val)
    if ival < 1:
        msg = '%r must be a positive number' % val
        raise argparse.ArgumentTypeError(msg)
    return ival


def _proc_count(val):
    if val == 'all':
        return val
    else:
        ival = int(val)
        return _positive_int(ival)


# ======================================================================================================================
# Override configs with cmd args
#
def _config_override():
    if not configs.has_section('USER'):
        configs.add_section('USER')
    if hasattr(cmd_args, 'dsa_file') and cmd_args.dsa_file is not None:
        configs.set('USER', 'dsa_param_file', str(cmd_args.dsa_file))
    if hasattr(cmd_args, 'chain_file') and cmd_args.chain_file is not None:
        configs.set('USER', 'chain_file', str(cmd_args.chain_file))
    if hasattr(cmd_args, 'blocks_dir') and cmd_args.blocks_dir is not None:
        configs.set('USER', 'blocks_dir', str(cmd_args.blocks_dir))
    if hasattr(cmd_args, 'num_proc') and cmd_args.num_proc is not None:
        configs.set('USER', 'num_processes', str(cmd_args.num_proc))
    if hasattr(cmd_args, 'mine_count') and cmd_args.mine_count is not None:
        configs.set('USER', 'mine_count', str(cmd_args.mine_count))
    if hasattr(cmd_args, 'chunk_size') and cmd_args.chunk_size is not None:
        configs.set('USER', 'chunk_size', str(cmd_args.chunk_size))


def init_cmd_args():
    cmd_parser = argparse.ArgumentParser(description=descriptions.intro, epilog=descriptions.examples,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = cmd_parser.add_subparsers(title=descriptions.subparsers_title,
                                           description=descriptions.subparsers_help)

    # parent parser for common functionalities
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--dsa_file', metavar='PATH', type=_valid_file, help=descriptions.path_dsa)
    parent_parser.add_argument('--chain_file', metavar='PATH', type=_valid_file, help=descriptions.path_chain)
    parent_parser.add_argument('--blocks_dir', metavar='PATH', type=_valid_dir,
                               help=descriptions.path_blocksdir)
    parent_parser.add_argument('--num_proc', metavar='N', type=_proc_count, help=descriptions.num_proc)

    # parser for "config"
    parser_conf = subparsers.add_parser('config', help=descriptions.config_title, description=descriptions.config_title,
                                        epilog=descriptions.config_defaults,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)
    conf_group = parser_conf.add_mutually_exclusive_group(required=True)
    conf_group.add_argument('--set', nargs=2, metavar=('valName', 'newVal'), action='append',
                            help=descriptions.config_set)
    conf_group.add_argument('--get', metavar='valName', help=descriptions.config_get)
    conf_group.add_argument('--reset', help=descriptions.config_reset, action='store_true')
    parser_conf.set_defaults(func=configure)

    # parser for "generate"
    parser_gen = subparsers.add_parser('generate', parents=[parent_parser], help=descriptions.generate_title,
                                       description=descriptions.generate_title)
    parser_gen.add_argument('-d', action='store_true', help=descriptions.generate_d)
    parser_gen.add_argument('-b', action='store_true', help=descriptions.generate_b)
    parser_gen.add_argument('-i', '--ignore_existing', action='store_true', help=descriptions.generate_ignore)
    parser_gen.add_argument('-f', '--fill_gaps', action='store_true', help=descriptions.generate_fill)
    parser_gen.add_argument('-c', '--count', type=_positive_int, help=descriptions.generate_count)
    parser_gen.set_defaults(func=generate)

    # parser for "mine"
    parser_mine = subparsers.add_parser('mine', help=descriptions.mine_title, description=descriptions.mine_title,
                                        parents=[parent_parser])
    parser_mine.add_argument('-n', '--no_generate', action='store_true', help=descriptions.mine_nogenerate)
    parser_mine.add_argument('-s', '--start_from', type=_positive_int, help=descriptions.mine_startfrom)
    parser_mine.add_argument('--mine_count', help=descriptions.mine_blockcount)
    parser_mine.add_argument('--chunk_size', type=_positive_int, help=descriptions.mine_chunksize)
    parser_mine.set_defaults(func=mine)

    # parser for "validate"
    parser_val = subparsers.add_parser('validate', parents=[parent_parser], help=descriptions.validate_title,
                                       description=descriptions.validate_title)
    parser_val.add_argument('-c', '--chain', action='store_true', help=descriptions.validate_chain)
    parser_val.add_argument('-t', '--transactions', action='store_true', help=descriptions.validate_trans)
    parser_val.set_defaults(func=validate)

    return cmd_parser


if __name__ == '__main__':
    freeze_support()

    # config file
    configs = ConfigParser.ConfigParser()
    configs.read('./config.ini')
    if not configs.has_section('USER'):
        configs.add_section('USER')

    # command arguments
    parser = init_cmd_args()
    cmd_args = parser.parse_args()

    # override default configs with cmd cmd_args
    _config_override()

    # ==================================================================================================================
    # acquire global parameters
    tx_len = configs.getint('DEFAULT', 'tx_len')
    link_len = configs.getint('DEFAULT', 'link_len')
    log_file = configs.get('DEFAULT', 'log_file')

    tx_count = 1 << (configs.getint('USER', 'tx_count').bit_length() - 1)
    if tx_count != configs.getint('USER', 'tx_count'):
        print 'WARNING: Entered tx_count, %r, is not a power of 2. ' \
              'Will be reduced to %r' % (configs.getint('USER', tx_count), tx_count)

    dsa_param_file = configs.get('USER', 'dsa_param_file')
    chain_file_name = configs.get('USER', 'chain_file')
    blocks_dir = configs.get('USER', 'blocks_dir')
    block_prefix = configs.get('USER', 'block_prefix')
    block_filename_template = block_prefix + '-%d.block'

    pow_len = configs.getint('USER', 'pow_len')
    chunk_size = configs.getint('USER', 'chunk_size')
    mine_count = float('inf') if configs.get('USER', 'mine_count') == 'infinite'\
        else configs.getint('USER', 'mine_count')
    try:
        num_processes = cpu_count() if configs.get('USER', 'num_processes') == 'all' \
            else configs.getint('USER', 'num_processes')
    except NotImplementedError:
        num_processes = 4
    # ==================================================================================================================

    cmd_args.func()
