#!/home/dd/anaconda3/bin/python

import myblockchain as myblock
import json

new_chain = myblock.Blockchain()

def add(mediabyte_str):
    new_chain.add_block(data=mediabyte_str)
        
def save_blockchain():
    with open("mediabyte_blockchain.json", "w") as f:
        for item in new_chain.chain:
            f.write(str(item))
            f.write("\n")


