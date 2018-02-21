"""
    Created by mbenlioglu on 2/6/2018
"""

# general descriptions
intro = '%(prog)s can generate random transaction blocks for the block chain based cryptocurrency, can calculate' \
        ' proof of works for the said blocks, and can validate the integrity of chain/blocks.'
examples = '''\
Examples
-----------------------------

python %(prog)s config --set num_proc 4   # Sets the default number of processors to 4
python %(prog)s generate -dbc 50          # Creates DSA parameters, then using these parameters
                                          # generates 50 transaction blocks

python %(prog)s mine                      # Continues mining starting from where it is left off
python %(prog)s validate -ct              # Validates longest chain file and all transactions 
'''

# common prefix/suffixes
_config_override = 'Overrides default settings and settings specified by "config --set". Execute "python %(prog)s' \
                   'config --help" for more information about settings'
_specify_path = 'Specify the path for '

# common path/config switches
path_dsa = '%(path_prefix)s DSA parameters file. %(config_override)s' % {'path_prefix': _specify_path,
                                                                         'config_override': _config_override}
path_blocksdir = '%(path_prefix)s blocks directory. %(config_override)s' % {'path_prefix': _specify_path,
                                                                            'config_override': _config_override}
path_chain = '%(path_prefix)s longest chain file. %(config_override)s' % {'path_prefix': _specify_path,
                                                                          'config_override': _config_override}
num_proc = 'Number of processors to be used. %(config_override)s' % {'config_override': _config_override}

# subparsers general help
subparsers_title = 'Available operations'
subparsers_help = 'Execute "%(prog)s {subcommand} --help" for more information about each of these subcommands'

# config
config_title = 'Sets/gets the defined values that will be used by other commands.'
config_defaults = '''\
Available options for setting
-----------------------------
num_processes    # Number of processors that will be used in the program. (default: 'all' or 4 if not available)
block_count      # Transaction block count to be mined. (default: 'infinite')
chunk_size       # Number of transaction blocks that are generated and mined in one step. (default: 100)
tx_count         # Number of transactions in every transaction block (default: 8)
pow_len          # Number of leading 0's in the proof of work hash (default: 6)
block_dir        # Path to the the directory in which transaction blocks are present. (default: ./blocks)
block_prefix     # Common prefix in file names of transaction block files. (default: TransactionBlock)
dsa_param_file   # Path of the file that consists DSA parameters (default: ./params.dsa)
chain_file       # Path of the file that consists the longest chain (default: ./longest.chain)
'''
config_set = 'Sets the value for the given parameter'
config_get = 'Retrieves the current value for given parameter'
config_reset = 'Reset the user defined values back to default settings.'

# generate
generate_title = 'Finds the most transaction with highest number, then creates specified number of transaction blocks' \
                 ' starting from that number.'
generate_d = 'Generates a DSA file with new DSA parameters, which will be used for newly generated transaction blocks'
generate_b = 'Generates new transaction blocks. When used with "-d", first new DSA parameters will be generated then' \
             ' new transactions will use new DSA parameters'
generate_ignore = 'Ignores and overrides existing block files having the same name convention'
generate_fill = 'Searches through the existing transaction blocks in the blocks directory and generates the missing' \
                ' transaction blocks'
generate_count = 'Number of blocks to be generated. Has no effect if "--fill_gaps" is defined'

# mine
mine_title = 'Calculates proof of work hashes of the transactions and records them to longest chain file.'
mine_nogenerate = 'Does not generate new transaction blocks if number of blocks in blocks directory is not sufficient' \
                  ' for given block count for mining.'
mine_startfrom = 'Ignores the log file and starts the mining process from the given transaction number or next' \
                 ' smallest transaction number if given number does not exist.'
mine_blockcount = 'Number of transaction blocks of which proof of works will be calculated.' \
                  ' %(config_override)s' % {'config_override': _config_override}
mine_chunksize = 'Number of transaction blocks that are generated and mined in one step. ' \
                 ' %(config_override)s' % {'config_override': _config_override}

# validate
validate_title = 'Validates integrity of longest chain and transactions.'
validate_chain = 'Validates that the proof of works in the longest chain file are correctly calculated.'
validate_trans = 'Confirms that transaction signatures and their corresponding hashes in longest chain file are valid'
