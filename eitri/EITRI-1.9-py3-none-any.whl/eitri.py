from EITRI.Account.account import account
from EITRI.Block.block import block
from EITRI.Network.network import network
from EITRI.Node.node import node
from EITRI.Transaction.transaction import transaction
from EITRI.Validator.validator import validator
from jsonrpc2 import JsonRpc

class eitri:

  def __init__ (self, **kwargs):
    self.ip = kwargs['ip']
    self.port = kwargs["port"]
    self.user = kwargs["user"]
    self.password = kwargs["password"]

    self.accounts = {}
    self.network = {}
    self.transaction = {}
    self.block = {}
    self.node = {}
    self.validator = {}
    
    self.setProvider()

  def __call__ (self):
    print('ip: {ip}, port: {port}, user: {user}, password: {password}'.format(
      ip = self.ip,
      port= self.port,
      user= self.user,
      password= self.password
    ))

  def setProvider (self):
    self.accounts = account()
    self.network = network()
    self.transaction = transaction()
    self.block = block()
    self.node = node()
    self.validator = validator()