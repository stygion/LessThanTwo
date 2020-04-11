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

# init web
app = VueFlask(__name__)
app.secret_key = '39fa7d3ccfba321b208706903d81ebcfcee30ecdfc578602'
socketio = SocketIO(app)

# init game
game = LessThanTwo()

##
# auxiliary 
##

def genPlayerId():
    return str(uuid4())

def pid():
  return session.get('pid')

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
  return render_template('gamemain.j2.html')

@app.route('/default/player/<pid>', methods=['DELETE'])
def delete_player(pid):
  print(f'delete player: {pid}')
  game.removePlayer(pid)
  return broadcastHead(game)

@app.route('/default/player/<pid>', methods=['DELETE'])
def rename_player(pid, new_name):
  print(f'rename_player({pid}, {new_name})' )
  game.renamePlayer(pid, new_name)
  return broadcastHead(game)

@app.route('/default/perspective')
def perspective():
  pid = session.get('pid')
  perspective = game.perspective(pid)
  return perspective

@app.route('/default/join', methods=['POST'])
def join():
  pid = session.get('pid')
  if request.method == 'POST' and pid:
    name = request.form.get('name')
    game.addPlayer(pid, name)
    broadcastHead(game)  
    # TODO proper return value
  return redirect('/')

##
# specific for LessThanTwo
##

@app.route('/default/reset', methods=['POST'])
def next_phase():
  body = request.json
  print(f'>>> next_phase, body = {body}')
  game.nextPhase()
  return broadcastHead(game)

@app.route('/default/guesser', methods=['PUT'])
def choose_guesser():
  newVal = request.json['newVal']
  print(f'>>> choose_guesser, newVal = {newVal}')
  game.setGuesser(newVal)
  return broadcastHead(game)

@app.route('/default/solution', methods=['PUT'])
def choose_solution():
  body = request.json
  print(f'>>> choose_solution, body = {body}')
  # TODO
  return broadcastHead(game)
   
@app.route('/default/clues', methods=['POST'])
def give_clue():
  body = request.json
  print(f'>>> give_clue, body = {body}')
  # TODO
  return broadcastHead(game)

@app.route('/default/guess', methods=['PUT'])
def make_guess():
  body = request.json
  print(f'>>> give_clue, body = {body}')
  # TODO
  return broadcastHead(game)



##
# start app
##

if __name__ == '__main__':
  host = config.get('server.host')
  port = config.get('server.port')
  socketio.run(app, host=host, port=int(port))