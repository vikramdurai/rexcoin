import hashlib
import random
import sqlite3

BLOCK_REWARD_BALANCER = 300
conn = sqlite3.connect("rexcoin.sqlite3")
c = conn.cursor()
c.execute("CREATE TABLE blocks (hash text, parent text, owner text)")
c.execute("""CREATE TABLE transactions (
    executor text,
    sender text,
    address text,
    amount real,
    proposed_rep real,
    reward real
    )""")
c.execute("""CREATE TABLE addresses (balance real, name text, index_ INTEGER, reputation real)""")
conn.commit()
conn.close()
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
    def store(self):
        conn = sqlite3.connect("rexcoin.sqlite3")
        c = conn.cursor()
        c.execute("INSERT INTO blocks VALUES (?, ?, ?)", 
            (self.hash, self.parent.hash, self.owner.name))
        c.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)",
            (
                self.hash,
                self.tx["sender"],
                self.tx["address"],
                self.tx["amount"],
                self.tx["proposed_rep"],
                self.tx["reward"]))
        conn.commit()
        conn.close()

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
        self.name.update(bytes(random.randint(0, 2**16)))
        self.name = "rex_" + self.name.hexdigest()
        Ledger.nodes.append(self)

    def update(self):
        Ledger.nodes.pop(self.index)
        Ledger.nodes.insert(self.index, self)
        conn = sqlite3.connect("rexcoin.sqlite3")
        c = conn.cursor()
        c.execute("UPDATE addresses SET balance = ?, reputation = ? WHERE name = ?", (
            self.balance, self.reputation, self.name
        ))
        conn.commit()
        conn.close()

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
        c.owner = self
        Ledger.blocks.append(c)
        self.registeredBlocks.append(c)
        self.update()
        c.store()


def findAddr(name):
    return [i for i in Ledger.nodes if i.name == name][0]