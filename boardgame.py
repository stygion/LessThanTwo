class Boardgame:

    def __init__(self):
        self.players = {}
        self.version = 1

    ##
    # player actions
    ##

    def addPlayer(self, player_id, player_name):
        self.players[player_id] = {
            'name': player_name
        }
        self.incVersion()

    def isKnownPlayer(self, player_id):
        return player_id and player_id in self.players

    def addPlayer(self, pid, name):
        self.players[pid] = {
            'name': name
        }
        self.incVersion()

    def removePlayer(self, player_id):
        if player_id in self.players:
            self.players.pop(player_id)    
        self.incVersion()

    def renamePlayer(self, player_id, new_name):
        if player_id in self.players:
            self.players[player_id]['name'] = new_name
        self.incVersion()

    def getPlayerName(self, player_id):
        if player_id in self.players:
            return self.players[player_id].get('name')
        return None

    ##
    # general purpose
    ##

    def incVersion(self):
        self.version += 1
        return self.version

    def head(self):
        return {
            'room': 'default',
            'version': self.version,
        }

    def perspective(self, viewer_pid):
        return {
            'version': self.version,
            'players': [
                { 
                    'pid': pid,
                    'name': player.get('name'),
                    'actions': {
                        'remove': {
                            'url': '/default/player/%s' % pid
                        },
                        'rename': {
                            'url': '/default/player/%s/name' % pid
                        }
                    },
                    'is_me': pid == viewer_pid,
                } for pid, player in self.players.items()
            ]
        }