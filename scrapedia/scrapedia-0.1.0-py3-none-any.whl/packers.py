"""The packers module holds all classes and functions related to turning
models into specific data structures.

ABCs: Packer

Classes: DataFramePacker
"""

import abc

import pandas as pd


class Packer(abc.ABC):
	"""An abstract base class for other packer classes to implement.

	Methods: pack
	"""
	@abc.abstractmethod
	def pack(self, models: tuple):
		"""Builds a data structure out of a list of model's.

		Parameters
		----------
		models: tuple -- the model list with the data

		Returns -- the data structure with the data
		"""
		pass


class DataFramePacker(Packer):
	"""A packer class specialized in building data frames out of models.

	Extends: Packer

	Methods: pack
	"""
	def __init__(self):
		"""DataFramePacker's constructor."""
		pass

	def pack(self, models: tuple) -> pd.DataFrame:
		"""Builds a data frame out of a list of model's.

		Parameters @Packer
		Returns @Packer
		"""
		idxs = [i[0] for i in models]
		data = [list(i[1:]) for i in models]
		columns = list(models[0]._fields[1:])

		return pd.DataFrame(data, index=idxs, columns=columns)
