import os, random
from flask import Flask, render_template, request, redirect
import redis
from plexapi.server import PlexServer
from flask_socketio import SocketIO, emit

#INSERT PLEX INFORMATION HERE
plexServerUrl = 'https://000-000-0-0.00000000000000000000000000000000.plex.direct:32400'        # Ensure plex direct URL is used
plexClientname = 'clientname'                                                                   # Ensure that client is online and on same network as Plex Server
plexToken = '[PLEX TOKEN]'                                                                      # https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
redisServer = 'plexvote_redis'                                                                  # redis container is setup by default

app = Flask(__name__)
app.secret_key = os.urandom(32)
socketio = SocketIO(app)

r = redis.StrictRedis(host=redisServer, port=6379, password='', decode_responses=True)

plex = PlexServer(plexServerUrl, plexToken)
movies = plex.library.section('Movies').all()
random.shuffle(movies)

i = 0

@app.route('/', methods=['GET', 'POST'])
def home():
    global i

    if request.method == 'POST':
        r.lpush('vote',request.form['vote'])

        if r.llen('vote') == 2:
            totalVotes = []
            while(r.llen('vote') != 0):
                totalVotes.append(r.lpop('vote'))

            if totalVotes[0] == 'yes' and totalVotes[1] == 'yes':
                #socketio.emit('agreement', 'agreement reached')

                votedMovie = plex.library.section('Movies').get(movies[i].title)
                client = plex.client(plexClientname)
                client.playMedia(votedMovie)
            else:
                if i < len(movies):
                    i = i + 1
                else:
                    i = 0
                
                socketio.emit('reloadPage')

                
    return render_template('index.html', movie = movies[i])
        

if __name__ == '__main__':
    socketio.run(app,debug=False, host='0.0.0.0', port='80')