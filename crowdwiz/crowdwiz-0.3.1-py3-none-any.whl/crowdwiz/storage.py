# -*- coding: utf-8 -*-
from graphenestorage import (
	InRamConfigurationStore,
	InRamEncryptedKeyStore,
	InRamPlainKeyStore,
	SqliteConfigurationStore,
	SqliteEncryptedKeyStore,
	SQLiteFile,
	SqlitePlainKeyStore,
)


url = "wss://crowdwiz.biz/ws"
# url = "ws://build.onbc.xyz:11011"
SqliteConfigurationStore.setdefault("node", url)
SqliteConfigurationStore.setdefault("order-expiration", 356 * 24 * 60 * 60)


def get_default_config_store(*args, **kwargs):
	if "appname" not in kwargs:
		kwargs["appname"] = "crowdwiz"
	return SqliteConfigurationStore(*args, **kwargs)


def get_default_key_store(config, *args, **kwargs):
	if "appname" not in kwargs:
		kwargs["appname"] = "crowdwiz"
	return SqliteEncryptedKeyStore(config=config, **kwargs)
