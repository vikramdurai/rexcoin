import hashlib
import random

class RexNoSuchAddress(Exception):
    def __init__(self, msg):
        super.__init__(msg)

class Block:
    def __init__(self):
        self.tx = []
        self.hash = ""
        self.validators = []

class Ledger:
    blocks = []
    pending = []
    nodes = []
    def registerTx(tx):
        if tx["address"] not in Ledger.nodes:
            raise RexNoSuchAddress("No such peer to send to")
        elif tx["sender"] not in Ledger.nodes:
            raise RexNoSuchAddress("No such sender to recieve from")
        else:
            Ledger.pending.append({**tx, "validators": []})

class Address:
    def __init__(self):
        self.balance = 0.000
        self.transactions = []
        self.registeredBlocks = []
        self.name = hashlib.sha256()
        self.name.update(bytes(str(random(0, 2**16)), "utf8"))
        self.name = "rex_"+self.name.hexdigest()
        Ledger.nodes.append(self)
    def pay(self, otheraddress, amount):
        Ledger.registerTx({
            "amount": amount,
            "sender": self.name,
            "address": self.otheraddress
        })
    def validate(self):
        pass