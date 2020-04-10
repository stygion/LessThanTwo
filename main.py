from vueflask import VueFlask
from flask import Flask, render_template, session, redirect, request
from flask_socketio import SocketIO

import json
import config
import game

player2sid = {}

app = VueFlask(__name__)
app.secret_key = '39fa7d3ccfba321b208706903d81ebcfcee30ecdfc578602'

socketio = SocketIO(app)

##
# auxiliary 
##

def pid():
  return session.get('pid')

##
# SocketIO 
##

@socketio.on('message')
def handle_my_event(msg):
  print('>>> Received client message: "%s"' % msg)

def updateAllClients(game):
  socketio.emit('player notification', game.stateHead())

##
# REST endpoints
##

@app.route('/default/player/<pid>', methods=['DELETE'])
def delete_player(pid):
  print(f'delete player: {pid}')
  game.removePlayer(pid)
  updateAllClients(game)
  return ''

@app.route('/default/player/<pid>', methods=['DELETE'])
def rename_player(pid, new_name):
  print(f'rename_player({pid}, {new_name})' )
  game.renamePlayer(pid, new_name)
  return ''

@app.route('/')
def index():
  return redirect('/default')

@app.route('/default')
def default():
  pid = session.get('pid')
  if not pid:
    pid = game.genPlayerId()
    print(f'>>> Created pid "{pid}"')
    session['pid'] = pid
  return render_template('gamemain.j2.html')

@app.route('/default/state')
def state():
  pid = session.get('pid')
  state = game.viewerState(pid)
  return state

@app.route('/default/join', methods=['GET', 'POST'])
def join():
  pid = session.get('pid')
  if request.method == 'POST' and pid:
    name = request.form.get('name')
    game.addPlayer(pid, name)
    updateAllClients(game)  
  return redirect('/')

if __name__ == '__main__':
  host = config.get('server.host')
  port = config.get('server.port')
  socketio.run(app, host=host, port=int(port))