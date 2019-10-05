class Playlist:
  ''' Represents a playlist of podcast episodes '''

  def __init__(self):
    self.episodes = []

  def addEpisode(self, episode):
    ''' Add an episode to this playlist '''
    self.episodes.append(episode)

  def addEpisodes(self, episodes):
    ''' Add a set of episodes to this playlist '''
    self.episodes.extend(episodes)

  def saveAsM3U(self, path):
    ''' Save this playlist to the file specified '''
    with open(path, 'w') as outfile:
      for episode in self.episodes:
        outfile.write("# {0}\n".format(episode.getTitle()))
        outfile.write(episode.getLink())
        outfile.write("\n")
