import web3
from web3 import Web3

class BlockCache :
    def __init__(self, w3, length=100, full_transactions=False) :
        self.blocks = {}
        self.head = None
        self.w3 = w3
        self.length = length # number of blocks to cache in memory
        # whether to call eth_getBlock with full transaction data or not
        if not isinstance(full_transactions, bool) :
            raise ValueError('full_transactions must be bool')
        self.full_transactions = full_transactions

    def _get_block(self, name) :
        blk = self.w3.eth.getBlock(name, self.full_transactions)
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

    def _canonical_chain(self) :
        # probably should call patch_holes -
        # not guaranteed that update has been called
        ret = []
        cur = self.head
        while cur :
            yield cur
            cur = self.blocks.get(cur.parentHash)

    @property
    def canonical_chain(self) :
        return list(self._canonical_chain())

    def is_canonical(self, blk) :
        return blk in self._canonical_chain()

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
