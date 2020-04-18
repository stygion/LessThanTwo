# web technologies
from vueflask import VueFlask
from flask import Flask, render_template, session, redirect, request, url_for
from flask_socketio import SocketIO

# misc vendor
import json
from uuid import uuid4

# custom
import config
from lessthantwo import LessThanTwo
from lessthantwo_web import LessThanTwo_WebAdapter

# init web
app = VueFlask(__name__)
app.secret_key = '39fa7d3ccfba321b208706903d81ebcfcee30ecdfc578602'
socketio = SocketIO(app)

# init game
game = LessThanTwo()
webadapter = LessThanTwo_WebAdapter(game)

##
# auxiliary 
##

def genPlayerId():
    return str(uuid4())

def pid():
  return session.get('pid')

def newVal():
  return request.json['newVal']

def broadcastHead(game):
  head = game.head()
  head['url'] = url_for('perspective')
  socketio.emit('player notification', head)
  return head

##
# SocketIO 
##

@socketio.on('message')
def handle_my_event(msg):
  print('>>> Received client message: "%s"' % msg)

##
# REST endpoints
##

@app.route('/')
def index():
  return redirect('/default')

@app.route('/default')
def default():
  pid = session.get('pid')
  if not pid:
    pid = genPlayerId()
    print(f'>>> Created pid "{pid}"')
    session['pid'] = pid
  default_name = session.get('player_name', 'Mysterious stranger')
  return render_template('gamemain.j2.html', default_name=default_name)

@app.route('/default/player/<pid>', methods=['DELETE'])
def delete_player(pid):
  print(f'delete player: {pid}')
  game.removePlayer(pid)
  return broadcastHead(game)

@app.route('/default/player/<pid>/name', methods=['DELETE'])
def rename_player(pid):
  value = newVal()
  print(f'rename_player({pid}, {value})' )
  session['player_name'] = value
  game.renamePlayer(pid, value)
  return broadcastHead(game)

@app.route('/default/game/clues/<pid>/hidden', methods=['PUT'])
def set_clue_hidden(pid):
  value = newVal()
  print(f'set_clue_hidden({pid}, {value})' )
  game.setClueHidden(pid, value)
  return broadcastHead(game)  

@app.route('/default/game', methods=['DELETE'])
def reset_game():
  print(f'reset_game()')
  game.reset()
  return broadcastHead(game)

@app.route('/default/game/perspective')
def perspective():
  pid = session.get('pid')
  perspective = webadapter.perspective(pid)
  return perspective

@app.route('/default/players', methods=['POST'])
def join():
  pid = session.get('pid')
  if request.method == 'POST' and pid:
    name = request.form.get('name')
    session['player_name'] = name    
    game.addPlayer(pid, name)
    broadcastHead(game)  
    # TODO proper return value
  return redirect('/')

##
# specific for LessThanTwo
##

@app.route('/default/reset', methods=['POST'])
def next_phase(): 
  print(f'>>> next_phase (current phase = {game.phase})')
  game.next_phase()
  return broadcastHead(game)

@app.route('/default/guesser', methods=['PUT'])
def choose_guesser():
  newVal = request.json['newVal']
  print(f'>>> choose_guesser, newVal = {newVal}')
  game.setGuesser(newVal)
  return broadcastHead(game)

@app.route('/default/solution', methods=['PUT'])
def choose_solution():
  newVal = request.json.get('newVal')
  print(f'>>> choose_solution, body = {newVal}')
  game.setSolution(newVal)
  return broadcastHead(game)
   
@app.route('/default/clues', methods=['POST'])
def give_clue():
  newVal = request.json.get('newVal')
  print(f'>>> give_clue, body = {newVal}')
  game.add_clue(pid(), newVal)
  return broadcastHead(game)

@app.route('/default/guess', methods=['PUT'])
def make_guess():
  newVal = request.json.get('newVal')
  print(f'>>> give_clue, body = {newVal}')
  game.makeGuess(newVal)
  return broadcastHead(game)



##
# start app
##

if __name__ == '__main__':
  host = config.get('server.host')
  port = config.get('server.port')
  socketio.run(app, host=host, port=int(port))