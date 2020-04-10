from uuid import uuid4

players = {}
version = 1

##
# player actions
##

def genPlayerId():
    return str(uuid4())

def addPlayer(player_id, player_name):
    players[player_id] = {
        'name': player_name
    }
    incVersion()

def isKnownPlayer(player_id):
    return player_id and player_id in players

def addPlayer(pid, name):
    players[pid] = {
        'name': name
    }
    incVersion()

def removePlayer(player_id):
    if player_id in players:
        players.pop(player_id)    
    incVersion()

def renamePlayer(player_id, new_name):
    if player_id in players:
        players[player_id]['name'] = new_name
    incVersion()

def getPlayerName(player_id):
    if player_id in players:
        return players[player_id].get('name')
    return None

##
# general purpose
##

def incVersion():
    global version
    version += 1
    return version

def stateHead():
    return {
        'room': 'default',
        'version': version,
    }

def viewerState(viewer_pid):
    return {
        'version': version,
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
            } for pid, player in players.items()
        ]
    }