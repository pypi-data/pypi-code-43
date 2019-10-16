"""Scrapedia's collection of scraper classes for fetching and parsing
Futpédia's soccer data and returning it as more easily accessible objects.

Classes: Scraper, SeasonScraper, ChampionshipScraper, RootScraper
"""

from .pipeline import DataStructure, PipelineFactory


class Scraper(object):
	"""Core of all of Scrapedia's scrapers."""
	def __init__(self, structure: DataStructure=DataStructure.DATA_FRAME,
				 retry_limit: int=10, backoff_factor: int=1,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""Scraper's constructor. Builds a pipeline factory for its subclasses
		usage.
		
		Parameters
		----------
		structure: DataStructure -- the data structure built at the end of the
		pipeline (default DataStructure.DATA_FRAME)
		retry_limit: int -- number of maximum retrying of requests on
		cases where the status code is in a given set (default 10)
		backoff_factor: int -- the number in seconds that serves as the wait
		time between failed requests, getting bigger on each failure
		(default 1)
		cache_maxsize: int -- maximum number of objects to be stored
		simultaneously on the internal cache (default 10)
		cache_ttl: int -- time to live in seconds for internal caching of
		data (default 300)
		"""
		self.structure = structure
		self.retry_limit = retry_limit
		self.backoff_factor = backoff_factor
		self.cache_maxsize = cache_maxsize
		self.cache_ttl = cache_ttl

		self._pipeline_factory = PipelineFactory(
			structure=structure, retry_limit=retry_limit,
			backoff_factor=backoff_factor, cache_maxsize=cache_maxsize,
			cache_ttl=cache_ttl
		)


class SeasonScraper(Scraper):
	"""Scraper that provides an interface to obtain data related to specific
	seasons of a championship.

	Methods: game, games
	"""
	def __init__(self, path: str,
				 structure: DataStructure=DataStructure.DATA_FRAME,
				 retry_limit: int=10, backoff_factor: int=1,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""SeasonScraper's constructor.
	
		Parameters
		----------
		path: str -- path of the season's web page
		Other parameters @scrapers.Scraper
		"""
		self.path = path

		super().__init__(
			structure=structure, retry_limit=retry_limit,
			backoff_factor=backoff_factor, cache_maxsize=cache_maxsize,
			cache_ttl=cache_ttl
		)

		self.games_pipeline = self._pipeline_factory.build('games')

	def games(self):
		"""Returns a data structure containing the season's games and their
		metadata.

		Returns -- games's home teams, home goals, away goals, away teams,
		stadiums, rounds, dates and paths
		"""
		return self.games_pipeline.scrap(self.path)


class ChampionshipScraper(Scraper):
	"""Scraper that provides an interface to obtain data related to specific
	championships.

	Methods: season, seasons
	"""
	def __init__(self, path: str,
				 structure: DataStructure=DataStructure.DATA_FRAME,
				 retry_limit: int=10, backoff_factor: int=1,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""ChampionshipScraper's constructor.
	
		Parameters
		----------
		path: str -- path of the championship's web page
		Other parameters @scrapers.Scraper
		"""
		self.path = path

		super().__init__(
			structure=structure, retry_limit=retry_limit,
			backoff_factor=backoff_factor, cache_maxsize=cache_maxsize,
			cache_ttl=cache_ttl
		)

		self.seasons_pipeline = self._pipeline_factory.build('seasons')

	def season(self, year: int):
		"""An easy access to build a new SeasonScraper using its year.

		Returns: SeasonScraper -- scraper built targeting the chosen
		season's web page
		"""
		if year < 0:
			raise ValueError(
				'The \'year\' parameter should be higher or equal to 0.')

		seasons = self.seasons()

		try:
			season = seasons.loc[year, :]
			return SeasonScraper(
				'{0}{1}'.format(self.path, season.get('path')),
				structure=self.structure,
				retry_limit=self.retry_limit,
				backoff_factor=self.backoff_factor,
				cache_maxsize=self.cache_maxsize, cache_ttl=self.cache_ttl
			)

		except Exception as err:
			raise ValueError(
				'The chosen year could not be found at the list of'
				' seasons.'
			)

	def seasons(self):
		"""Returns a data structure containing the championship's seasons and
		their metadata.

		Returns -- seasons's years, start date, end date, number of goals and
		number of games
		"""
		return self.seasons_pipeline.scrap(self.path)


class RootScraper(Scraper):
	"""Scraper that provides easy access to common Futpédia's resources like
	lists of teams, games and championships.

	Methods: championship, championships, teams
	"""
	def __init__(self, structure: DataStructure=DataStructure.DATA_FRAME,
				 retry_limit: int=10, backoff_factor: int=1,
				 cache_maxsize: int=10, cache_ttl: int=300):
		"""RootScraper's constructor. Builds a pipeline used to fetch
		Futpédia's data concerning teams and championships.
	
		Parameters @Scraper
		"""
		super().__init__(
			structure=structure, retry_limit=retry_limit,
			backoff_factor=backoff_factor, cache_maxsize=cache_maxsize,
			cache_ttl=cache_ttl
		)

		self._champs_pipeline = self._pipeline_factory.build('championships')
		self._teams_pipeline = self._pipeline_factory.build('teams')

	def championship(self, id_: int) -> ChampionshipScraper:
		"""An easy access to build a new ChampionshipScraper using its ID.

		Returns: ChampionshipScraper -- scraper built targeting the chosen
		championship's web page
		"""
		if id_ < 0:
			raise ValueError(
				'The \'id_\' parameter should be higher or equal to 0.')

		champs = self.championships()

		try:
			champ = champs.iloc[id_, :]
			return ChampionshipScraper(
				champ.get('path'), structure=self.structure,
				retry_limit=self.retry_limit,
				backoff_factor=self.backoff_factor,
				cache_maxsize=self.cache_maxsize, cache_ttl=self.cache_ttl
			)

		except Exception as err:
			raise ValueError(
				'The chosen id could not be found at the list of'
				' championships.'
			)

	def championships(self):
		"""Returns a data structure containing Futpédia's championships and
		their metadata.

		Returns -- championship's ids, names and paths
		"""
		return self._champs_pipeline.scrap('/')

	def teams(self):
		"""Returns a data structure containing Futpédia's teams and their
		metadata.

		Returns -- teams's ids, names and paths
		"""
		return self._teams_pipeline.scrap('/times')
