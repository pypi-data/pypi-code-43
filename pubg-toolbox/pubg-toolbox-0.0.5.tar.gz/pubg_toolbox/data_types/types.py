class PUBGDataParser:
    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.get_id())

    def get_id(self):
        return 'No ID'

    def get_type(self):
        return self.data_type

class Player(PUBGDataParser):
    def __init__(self, raw_data):
        data = raw_data['data'][0]

        self.data_type = data.get('type')
        self.account_id = data.get('id')
        self.attributes = data.get('attributes')
        self.player_name = self.attributes.get('name')

        self.matches = data['relationships']['matches']['data']

    def get_id(self):
        return self.account_id

    def get_matches(self):
        return self.matches

class Season(PUBGDataParser):
    def __init__(self, data):
        self.data_type = data['type']
        self.season_id = data['id']
        attributes = data['attributes']
        self.is_current_season = attributes['isCurrentSeason']

    def get_id(self):
        return self.season_id

class Match(PUBGDataParser):
    def __init__(self, raw_data):
        data = raw_data['data']
        self.data_type = data['type']
        self.match_id = data['id']

        attributes = data['attributes']
        self.match_map = attributes['mapName']
        self.game_mode = attributes['gameMode']
        self.created_at = attributes['createdAt']

        included = raw_data['included']
        assets = list(filter(lambda item: item.get('type') == 'asset', included))
        if len(assets) <= 0:
            self.telemetry_url = None
        else:
            self.telemetry_url = assets[0]['attributes']['URL']

    def get_id(self):
        return self.match_id

    def get_match_map(self):
        return self.match_map

    def get_game_mode(self):
        return self.game_mode

    def get_telemetry_url(self):
        return self.telemetry_url

class Seasons:
    def __init__(self, raw_data):
        data = raw_data['data']
        self.seasons = []
        for d in data:
            season = Season(d)
            if season.is_current_season:
                self.current_season = season
            self.seasons.append(season)

    def get_all_seasons(self):
        return self.seasons

    def get_current_season(self):
        return self.current_season

class Matches:
    GAME_MODES = [
            'matchesSolo',
            'matchesDuo',
            'matchesSquad',
            'matchesSoloFPP',
            'matchesDuoFPP',
            'matchesSquadFPP',
            ]
    def __init__(self, raw_data):
        data = raw_data['data']
        self.matches = {}
        relationships = data.get('relationships')

        for mode in self.GAME_MODES:
            self.matches[mode] = []
            matches_data = relationships.get(mode)['data']

            for md in matches_data:
                self.matches[mode].append(md['id'])

    def get_matches(self, game_mode):
        return self.matches.get(game_mode)

