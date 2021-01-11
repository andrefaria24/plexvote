import os, random
from flask import Flask, render_template, request, redirect
import redis
from plexapi.server import PlexServer
from flask_socketio import SocketIO, emit

#PLEX INFORMATION
plexServerUrl = 'https://000-000-0-0.00000000000000000000000000000000.plex.direct:32400'        # Ensure plex direct URL is used
plexToken = '[PLEX TOKEN]'                                                                      # https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
voterCount = 2                                                                                  # Amount of voting users
plexClientname = 'clientname'                                                                   # Ensure that client is online and on same network as Plex Server
redisServer = 'plexvote_redis'                                                                  # redis container is setup by default
#END PLEX INFORMATION

app = Flask(__name__)
app.secret_key = os.urandom(32)
socketio = SocketIO(app)

r = redis.StrictRedis(host=redisServer, port=6379, password='', decode_responses=True)

plex = PlexServer(plexServerUrl, plexToken)
movies = plex.library.section('Movies').all()
random.shuffle(movies)

i = 0

@app.route('/', methods=['GET'])
def home():
    global i

    return render_template('index.html', movie = movies[i])

@app.route('/vote', methods=['POST'])
def vote():
    global i

    r.lpush('vote', request.form['btnVote'])

    if r.llen('vote') < voterCount:
        #return ('', 204)        #Return no content
        return render_template('waiting.html')
    else:
        totalVotes = []
        while(r.llen('vote') != 0):
            totalVotes.append(r.lpop('vote'))

        if totalVotes[0] == 'yes' and totalVotes[1] == 'yes':
            print("Playing " + movies[i].title + " on " + plexClientname)

            votedMovie = plex.library.section('Movies').get(movies[i].title)
            client = plex.client(plexClientname)
            client.playMedia(votedMovie)
            
            socketio.emit('reloadPage', broadcast = True)
        else:
            if i < len(movies):
                i = i + 1
            else:
                i = 0
            
            socketio.emit('reloadPage', broadcast = True)

        return render_template('index.html', movie = movies[i])
        


if __name__ == '__main__':
    socketio.run(app,debug=False, host='0.0.0.0', port='80')