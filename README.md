### README
This is a simple Python class based on web3.py to help keep track of the
canonical Ethereum chain (and orphans) - which is a requirement for coding
correct applications in the presence of reorgs.

#### Install
```
pip install git+https://github.com/charles-cooper/block-cache.git
```

#### Example Usage
[example.py](example.py):
```python
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
        print(len(blks.canonical_chain))
        end = time.time()
        print('%r seconds' % str(end - start))

    time.sleep(1)
```
