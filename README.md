## BiTPy

This project simulates the Peer-to-Peer communication protocol using the Rarest-First algorithm. Albeit it is under development, it works fine right now! As it contains good topics to work with, it can be helpful for many people. In this project, we cover different materials, such as :

- [Socket programming](https://docs.python.org/3/howto/sockets.html).
- [Parallel processing](https://docs.python.org/3/library/threading.html).
- [HTTP request handling](https://docs.python.org/3/library/http.client.html).
- [File working](https://docs.python.org/3/library/fileinput.html).
- ...

## What is Peer-to-Peer communication?
Peer-to-Peer communication is one of the most common protocols for transferring large files, such as digital video files containing TV shows and video clips or digital audio files containing songs.\
To send or receive files, a person uses a client on their Internet-connected computer. A client is a computer program that implements the Peer-to-Peer communication protocol. Trackers provide a list of files for transfer and allow the client to find peer users, known as "seeds," who may transfer the files.\
Programmer Bram Cohen, a University at Buffalo alums, designed this protocol in April 2001 and released the first available version on 2 July 2001.\
The Peer-to-Peer communication protocol can reduce servers and network congestion while distributing large files. Rather than downloading a file from a single server, the Peer-to-Peer communication protocol allows users to join a "swarm" of hosts to upload to or download from each other simultaneously. The protocol is an alternative to the older single source, multiple mirror sources technique for distributing data and can work effectively over networks with lower bandwidth. Using this protocol, several basic computers, such as home computers, can replace large servers while efficiently distributing files to many recipients. This lower bandwidth usage also helps prevent large spikes in internet traffic in a given area, keeping internet speeds higher for all users, regardless of whether or not they use the BitTorrent protocol.

## Using the project :
1. Clone it
2. Place your files in the "/files" directory.
3. Run tracker.py
4. Run peer.py
    - Run peer as a seeder for every file you want a swarm for.
    - Run peer as leecher for every peer adding to a swarm.

## Contact me
[My Page](http://ee.sharif.edu/~soroush.nourzad)
