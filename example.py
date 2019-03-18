#!/usr/bin/env python
from blockcache import BlockCache
from web3 import Web3
import time
import sys

w3 = Web3()

if w3.eth.syncing :
    sys.stderr.write('Connected, syncing...\n')
    while w3.eth.syncing :
        time.sleep(1)
    sys.stderr.write('Synced!\n')
else :
    sys.stderr.write('Connected.\n')

blks = BlockCache(w3, length=10)
blks.ensureHead()
print(blks.head.number)

while True :
    start = time.time()

    holes, pruned = blks.update()

    if holes :
        print('HOLES ' + str([(b.hash, b.number) for b in holes]))
        print('PRUNED ' + str([(b.hash, b.number) for b in pruned]))
        print(len(list(blks.canonical_chain)))
        #for x in pruned :
        #    print(f'{x.hash} is canonical: {blks.is_canonical(x)}')
        end = time.time()
        print('%r seconds' % str(end - start))

    time.sleep(1)
