A web application that will help decide what movie to watch from a given Plex movie library once a general consent is established based on user votes (currently only working for two voters).

The application will select a random movie from a given Plex library. It will then receive client submited votes (yes or no) and store them into a redis queue. Once an agreement is reached on what movie to watch, the chosen movie is streamed to a selected device.

Technologies used:
Flask
PlexAPI (Python bindings)
SocketIO
Redis
Docker + Docker Compose for containerization