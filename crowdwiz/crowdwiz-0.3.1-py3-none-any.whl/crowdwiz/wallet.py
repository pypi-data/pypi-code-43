# -*- coding: utf-8 -*-
from crowdwizbase.account import PrivateKey
from graphenecommon.wallet import Wallet as GrapheneWallet
from graphenecommon.exceptions import (
	InvalidWifError,
	KeyAlreadyInStoreException,
	KeyNotFound,
	NoWalletException,
	OfflineHasNoRPCException,
	WalletExists,
	WalletLocked,
)
from .instance import BlockchainInstance


@BlockchainInstance.inject
class Wallet(GrapheneWallet):
	def define_classes(self):
		# identical to those in crowdwiz.py!
		self.default_key_store_app_name = "crowdwiz"
		self.privatekey_class = PrivateKey
