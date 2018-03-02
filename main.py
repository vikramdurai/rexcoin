import hashlib
import random


BLOCK_REWARD_BALANCER = 300

class RexNoSuchAddress(Exception): pass
class RexNotEnoughCoins(Exception): pass

def randf(start=0.000000, limit=0.000000):
    x = random.random()
    while not ((x > start) and (x < limit)):
        x = random.random()
    return x

class Block:
    def __init__(self):
        self.tx = {}
        self.hash = ""
        self.parent = None
        self.owner = None

def genesisBlock():
    x = Block()
    x.hash = "8f27f432fcbaa4b5180a1cc7a8fa166a93cda3c1bce6f19922dd519d02f4bb39"
    return x

class Ledger:
    blocks = [genesisBlock()]
    pending = []
    nodes = []

    def registerTx(tx):
        if findAddr(tx["address"]) not in Ledger.nodes:
            raise RexNoSuchAddress("No such peer to send to")
        elif findAddr(tx["sender"]) not in Ledger.nodes:
            raise RexNoSuchAddress("No such sender to recieve from")
        elif tx["amount"] >= findAddr(tx["sender"]).balance:
            raise RexNotEnoughCoins("Not enough coins to perform requested transaction")
        else:
            Ledger.pending.append({
                **tx, 
                "proposed_rep": randf(limit=0.000005),
                "reward": 0.005})

class Address:
    def __init__(self):
        self.balance = 0.000
        self.transactions = []
        self.registeredBlocks = []
        self.name = hashlib.sha256()
        self.index = len(Ledger.nodes)
        self.reputation = 0.000000
        self.name.update(bytes(str(random.randint(0, 2**16)), "utf8"))
        self.name = "rex_" + self.name.hexdigest()
        Ledger.nodes.append(self)

    def update(self):
        Ledger.nodes.pop(self.index)
        Ledger.nodes.insert(self.index, self)

    def pay(self, otheraddress, amount):
        tx = {
            "amount": amount,
            "sender": self.name,
            "address": otheraddress
        }
        self.transactions.append(tx)
        Ledger.registerTx(tx)

    def validate(self):
        x = Ledger.pending.pop()
        a = findAddr(x["sender"])
        b = findAddr(x["address"])
        a.balance -= x["amount"]
        a.update()
        b.balance += x["amount"]
        b.update()
        self.reputation += x["proposed_rep"]
        self.balance += self.reputation * (x["reward"] / BLOCK_REWARD_BALANCER)
        c = Block()
        c.tx = x
        c.hash = hashlib.sha256()
        c.hash.update(bytes(str(self.balance)
            + str(self.reputation)
            + self.name
            + str(len(self.registeredBlocks))
            + str(len(self.transactions)), "utf8"))
        c.hash = c.hash.hexdigest()
        c.parent = Ledger.blocks[len(Ledger.blocks)-1]
        c.owner = self.name
        Ledger.blocks.append(c)
        self.registeredBlocks.append(c)
        self.update()


def findAddr(name):
    return [i for i in Ledger.nodes if i.name == name][0]