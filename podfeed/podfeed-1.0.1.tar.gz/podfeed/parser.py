import feedparser
import time
from urllib.request import urlopen
import math
from os.path import basename
import re
from logging import getLogger
LOGGER = getLogger('podfeed')

TRACK_REGEX = re.compile(r'^.*\.(mp3|wav|aif.?|flac|ogg|wma|m4a|aac)$')

def validTrackLink(link):
  ''' Return true if the link appears to be a valid link. '''
  filename = basename(link).split("?")[0]
  return TRACK_REGEX.match(filename)

def isNewEntry(entry, date):
  ''' Return true if this entry was published after the given date. '''
  published = time.mktime(entry['published_parsed'])
  return published >= date

class Episode:
  ''' Represents a single entry in the RSS feed containing a link. '''
  CHUNK_SIZE = 32*1024

  def __init__(self, title, date, link):
    self.title = title
    self.date = date
    self.link = link
    self.ext = link.split(".")[-1]

  def download(self):
    ''' Download this episode and return it as a request object '''
    return urlopen(self.link)

  def write(self, file_obj):
    ''' Download this episode and write it to the specified object '''

    with self.download() as response:
      try:
        chunk = response.read(self.CHUNK_SIZE)
        while chunk:
          file_obj.write(chunk)
          chunk = response.read(self.CHUNK_SIZE)

      except Exception as err:
        LOGGER.error("Could not write file: {0}".format(err))

  def writeFile(self, path):
    ''' Download this episode and write it to the specified filename '''
    LOGGER.debug("Writing {0}...".format(path))

    with self.download() as response:
      with open(path, 'wb') as outfile:
        self.write(outfile)

  def getLink(self):
    ''' Return the link for this episode '''
    return self.link

  def getTitle(self):
    ''' Return the title for this episode '''
    return self.title

  def getDate(self):
    ''' Retrurn the publish date for this episode '''
    return self.date

  def getExt(self):
    ''' Return the extension for this episode (ex: mp3) '''
    return self.ext

class StandardFeedParser:
  ''' StandardFeedParser is a base class used to parse an RSS feed and identify,
      extract, and download episode files from it. It will download a feed,
      parse new entries from it, and return those entries packaged in Episode
      objects.
  '''
  CHUNK_SIZE = 32*1024

  def __init__(self, url):
    self.url = url

  def getNewEpisodes(self, date):
    ''' Gather new episodes for this feed. '''
    LOGGER.debug("Running {0}".format(self.url))

    data = feedparser.parse(self.url)
    episodes = []

    if ('feed' in data) and ('title' in data.feed) and ('entries' in data):
      title = re.sub("\W", "", data.feed.title)
      entries = data['entries']

      for entry in entries:
        if (date == None) or (isNewEntry(entry, date)):
          try:
            episode = self.makeEpisode(title, entry)            
            episodes.append(episode)

          except Exception as e:
            LOGGER.warning("An error occured while parsing an entry from "+
              "{0}. This entry will be ignored: {1}".format(self.url, e))
    else:
      LOGGER.error("The data returned from feed URL "+
        "{0} was invalid: {1}".format(self.url, data))

    LOGGER.debug("Processed {0} entries for {1}".format(
      len(episodes), self.url))

    return episodes

  def makeEpisode(self, title, entry):
    ''' Create an Episode object for this entry '''
    published_time = math.floor(time.mktime(entry['published_parsed']))
    link = self.getTrackLink(entry)

    if link != None:
      episode = Episode(title, published_time, link)
      return episode

    else:
      raise Exception("No link was found.")

  def getTrackLink(self, entry):
    ''' Extract a link to an MP3 file from this entry. By default, this method
    searches the "links" section of an entry for one that looks like an MP3.
    If none is found, returns None. '''
    track_link = None

    if ('links' in entry) and (len(entry.links) > 0):
      for link in entry.links:
        if ('href' in link) and validTrackLink(link.href):
          track_link = link.href

    return track_link

def parseFeed(url, date, parser=StandardFeedParser):
  ''' Parses the feed given by <url>, and returns episodes posted after <date>.
      Uses <parser> to extract URLs from the entries; defaults to
      StandardFeedParser. '''
  p = parser(url)
  return p.getNewEpisodes(date)
