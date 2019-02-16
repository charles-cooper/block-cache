#!/usr/bin/env python

import datetime

import web3
from web3 import Web3

class BlockCache :
    def __init__(self, w3, length=100) :
        self.blocks = {}
        self.head = None
        self.w3 = w3
        self.length = length # number of blocks to cache in memory

    def _get_block(self, name) :
        blk = self.w3.eth._get_block(name)
        self.blocks[blk.hash] = blk
        return blk

    # Returns a block if updated
    def _update_head(self) :
        blk = self._get_block('latest')
        if self.head != blk :
            self.head = blk
            return self.head
        return None

    # Returns a block if there was no head
    def ensureHead(self) :
        if not self.head :
            return self._update_head()
        return None

    def update(self) :
        holes = []
        newHead = self._update_head()
        if newHead :
            holes.append(self.head)
        holes.extend(self._patch_holes())
        rmed = self.prune()
        return holes, rmed

    @property
    def canonical_chain(self) :
        # probably should call patch_holes -
        # not guaranteed that update has been called
        ret = []
        cur = self.head
        while cur :
            ret.append(cur)
            cur = self.blocks.get(cur.parentHash)
        return ret

    def is_canonical(self, blk) :
        return blk in self.canonical_chain()

    def is_prunable(self, blk) :
        return blk.number <= self.head.number - self.length

    def prune(self) :
        rm = []
        for blk in self.blocks.values() :
            if self.is_prunable(blk) :
                rm.append(blk)
        for blk in rm :
            del self.blocks[blk.hash]
        return rm

    # Returns hash of block if less than self.length blocks behind
    # head, and is also not in memory.
    # @pure
    # TODO refactor to generator
    def _find_hole(self, start=None) :
        if start is None :
            cur = self.head
        else :
            cur = start

        while cur.number - 1 > self.head.number - self.length :
            parent = self.blocks.get(cur.parentHash)
            if parent is None :
                return cur.parentHash
            cur = parent

        return None

    # Returns the holes that needed to be patched in.
    def _patch_holes(self) :
        blk = None
        holes = []

        while True :

            hole = self._find_hole(blk)
            if not hole :
                break

            blk = self._get_block(hole)
            holes.append(blk)

        return holes

if __name__ == '__main__' :
    import asyncio
    import time
    import sys

    async def aio_main() :
        w3 = Web3()

        if w3.eth.syncing :
            sys.stderr.write('Connected, syncing...\n')
            while w3.eth.syncing :
                time.sleep(1)
            sys.stderr.write('Synced!\n')
        else :
            sys.stderr.write('Connected.\n')

        blks = RecentBlocks(w3, 10)
        blks.ensure_head()
        print(blks.head.number)

        while True :
            start = time.time()

            holes, pruned = blks.update()
            if holes :
                print('HOLES ' + str([(b.hash, b.number) for b in holes]))
                print('PRUNED ' + str([(b.hash, b.number) for b in pruned]))
                print(len(blks.canonical_chain()))
                end = time.time()
                print('%r seconds' % str(end - start))

            await asyncio.sleep(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(aio_main())