from hashlib import sha256


def update_hash(*args):
    hashing_str = "";
    h = sha256()
    for arg in args:
        hashing_str += str(arg)

    h.update(hashing_str.encode('utf-8'))
    return h.hexdigest()


print(update_hash("zbat"))


class Block():

    def __init__(self, number=0, previous_hash="0" * 64, data=None, nonce=0):
        self.data = data
        self.number = number
        self.previous_hash = previous_hash
        self.nonce = nonce

    def zbathash(self):
        return update_hash(self.previous_hash, self.number, self.data, self.nonce)

    def __str__(self):
        return str("::Block#%s\n::Hash %s\n::Previous %s\n::Data %s\n::Nonce %s" % (
            self.number, self.zbathash(), self.previous_hash, self.data, self.nonce))


class Blockchain():
    miningdifflvl = 3

    def __init__(self):
        self.chain = []

    def push_block_to_chain(self, block):
        self.chain.append(block)

    def pop_block_from_chain(self, block):
        self.chain.remove(block)

    def mine(self, block):
        try:
            block.previous_hash = self.chain[-1].zbathash()
        except IndexError:
            pass

        while True:
            if block.zbathash()[:self.miningdifflvl] == "0" * self.miningdifflvl:
                self.push_block_to_chain(block)
                break
            else:
                block.nonce += 1

    def isvalid(self):
        for i in range(1, len(self.chain)):
            _previous = self.chain[i].previous_hash
            _current = self.chain[i - 1].zbathash()
            if _previous != _current or _current[:self.miningdifflvl] != "0" * self.miningdifflvl:
                return False

        return True


def main():
    blockchain = Blockchain()
    block_data = ["Zbat", "Crypto", "Tanit", "Doge", "Zbatcoin"]
    nbr = 0
    for data in block_data:
        nbr += 1
        blockchain.mine(Block(nbr, data))

    # print(blockchain.chain)
    for block in blockchain.chain:
        print(block)

    blockchain.chain[2].data = "corrupt data"
    blockchain.mine(blockchain.chain[2])

    print(blockchain.isvalid())
    # block = Block("zbat", 1)


if __name__ == '__main__':
    main()
