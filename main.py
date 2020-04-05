from flask import Flask, render_template, session, redirect, request
from uuid import uuid4

app = Flask(__name__)
app.secret_key = '39fa7d3ccfba321b208706903d81ebcfcee30ecdfc578602'

players = {}

@app.route('/')
def index():
  player_id = session.get('player_id')
  if not player_id or player_id not in players:
    return redirect('/join')

  handle = players[player_id].get('handle')
  return render_template('gamemain.j2.html', handle=handle, players=players)


@app.route('/join', methods=['GET', 'POST'])
def join():
  player_id = session.get('player_id')
  if player_id and request.method == 'POST':
    players[player_id] = {
      'handle': request.form.get('handle')
    }
    return redirect('/')

  if request.method == 'GET':
    player_id = str(uuid4())
    print('>> Created player_id "%s"' % player_id)
    session['player_id'] = player_id
    return render_template('join.j2.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port='3000')