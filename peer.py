# ######################################
# TODO :    SOROOSH NOORZAD - 99205372
# ######################################

# ######################################
# TODO :   Import libraries
# ######################################
import os
import sys
import time
import json
import base64
import socket
import hashlib
import requests
import threading
import numpy as np
import pandas as pd
from os import walk
from random import randint


# below libraries probably can be removed from here
import datetime
import bencodepy  # pip install bencode.py



# ######################################
# TODO  :   Classes and functions
# ######################################
from functions import *


def respond(client_socket):
    while True:
        received_msg = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
        if received_msg == 'connect':
            client_socket.send(bytes("unchoke", FORMAT))
            piece_number = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
            seeds = pd.read_csv(peer_seeds_DB, delimiter=',')
            index_counts = len(seeds.index)
            exist = False
            for j in range(index_counts):
                if int(piece_number) == seeds["number"][j]:
                    exist = True
            if exist:
                piece = seeds['piece'][int(piece_number)-1]
                piece_size = len(piece)
                client_socket.send(bytes(str(piece_size), FORMAT))
                ok = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                if ok == "ok":
                    bytes_to_send = [piece[i:i + BUFFER_SIZE] for i in range(0, len(piece), BUFFER_SIZE)]
                    for j in range(len(bytes_to_send)):
                        client_socket.send(bytes(str(bytes_to_send[j]), FORMAT))
                else:
                    print('not ok!')
            else:
                print('not exist')
        else:
            print("not connect")
            client_socket.close()
            break


class SeedMode:
    def __init__(self):
        # INITIALISING :
        # creating an INET socket (IPV4 socket) with Streaming mode(TCP connections)
        # socket.SOCK_DGRAM is for UDP(user datagram protocol)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state.
        # TIME_WAIT indicates that local endpoint (this side) has closed the connection.
        # The connection is being kept around so that any delayed packets can be matched to
        # the connection and handled appropriately. The connections will be removed when
        # they time out within four minutes.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Set the listening porn on server for incoming connections
        server_socket.bind((myOwnIP, myOwnPort))
        # we want it to queue up as many as q connect requests (the normal max is 5)
        # before refusing outside connections. If the rest of the code is written
        # properly, q = 5 should be plenty.
        q = 5
        server_socket.listen(q)
        print("Seed Mode. Listening at ", (myOwnIP, myOwnPort))
        while True:
            # Waiting mode. Wait until accept connections from outside
            client_socket, peer_address = server_socket.accept()
            listening_ip = client_socket.getsockname()[0]
            listening_port = client_socket.getsockname()[1]
            # Incoming is the one who wants to connect server. = peer_address
            incoming_ip = client_socket.getpeername()[0]
            incoming_port = client_socket.getpeername()[1]
            print("Established: ", (incoming_ip, incoming_port), "->", (listening_ip, listening_port))
            logger(myOwnID, "IN___CONN", "Established: "
                   + incoming_ip + ":" + str(incoming_port) + "->" + listening_ip + ":" + str(listening_port))
            # # We response using thread.
            c_thread = threading.Thread(target=respond, args=(client_socket,))
            c_thread.daemon = True
            c_thread.start()


class LeechMode:
    def __init__(self, p_ip, p_port, list_to_take):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # clientSock.bind((myOwnIP, myOwnPort)) # We don't want to set outgoing port. It's random! but we could!
            client_socket.connect((p_ip, p_port))
            print("Connected: ", (myOwnIP, myOwnPort), " -> ", (p_ip, p_port))
            while len(list_to_take) > 0:
                print("download piece #", list_to_take[0])
                client_socket.send(bytes("connect", FORMAT))
                received_data = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                if received_data == "unchoke":
                    client_socket.send(bytes(str(list_to_take[0]), FORMAT))
                    chunk_size = client_socket.recv(BUFFER_SIZE).decode(FORMAT)
                    client_socket.send(bytes("ok", FORMAT))
                    piece_data = str(client_socket.recv(BUFFER_SIZE).decode(FORMAT))
                    received_size = len(piece_data)
                    while received_size < int(chunk_size):
                        piece_data = piece_data + str(client_socket.recv(BUFFER_SIZE).decode(FORMAT))
                        received_size = len(piece_data)
                        percent = int((received_size/float(chunk_size)) * 100)
                        print(str(percent) + "% of piece #" + str(list_to_take[0]) + " downloaded!") if percent < 100 else False
                        time.sleep(0.2)
                        # os.system('cls||clear')
                    # For testing
                    # with open("_AAA.txt", "w") as AAA:
                    #     AAA.write(piece_data)
                    check_sha1 = hashlib.sha1()
                    piece_data = piece_data.encode(FORMAT)

                    check_sha1.update(piece_data)
                    check_hash = check_sha1.hexdigest()
                    pieces_hash = str_to_list(Dictionary['info']['pieces'], "str")
                    # print(list_to_take[0])
                    # print(pieces_hash[list_to_take[0]-1])
                    # if pieces_hash[list_to_take[0]-1] == check_hash:
                    print("Piece #" + str(list_to_take[0]) + " downloaded!")
                    add_seed = pd.read_csv(peer_seeds_DB, delimiter=',')
                    # Add chunk in !
                    received_seed = \
                        np.array([[list_to_take[0], file_to_leech_name, piece_data, check_hash]])
                    add_seed = add_seed.append(
                        pd.DataFrame(received_seed, columns=['number', 'file_name', 'piece', 'piece_hash']))
                    add_seed.to_csv(peer_seeds_DB, index=False)
                    del list_to_take[0]
                    # else:
                    #     print('hash err')
                    #     time.sleep(10)
                else:
                    print('choke err')
                    time.sleep(10)
            new_file_parts = pd.read_csv(peer_seeds_DB, delimiter=',')
            new_file_parts.sort_values(by=["number"], ascending=True)
            index_counts = len(new_file_parts.index)
            with open(myOwnID + " - " + file_to_leech_name, "wb") as new_file:
                for j in range(index_counts):
                    binary = new_file_parts["piece"][j]
                    binary = base64.b64decode(binary)
                    new_file.write(binary)
            # base64_message = base64_bytes.decode('ascii')
            logger(myOwnID, "GOT___ALL", "All the pieces taken")
            print('All gotten. Nothing to leech anymore.')
            client_socket.close()


def request_tracker():
    logger(myOwnID, "REQ__TRAK", "Leecher will request tracker for our swarm members identity.")
    # What I have? current seeds!
    current_seeds = pd.read_csv(peer_seeds_DB, delimiter=',')
    index_counts = len(current_seeds.index)
    # row_count, column_count = current_seeds.shape
    csn = '{'  # csn : current seeds numbers
    if index_counts >= 1:
        for j in range(index_counts):
            csn = csn + str(current_seeds["number"][j]) + ','
        csn = csn[:-1] + '}'
    else:
        csn = csn + '}'

    # sending get request and saving the response as response object
    payload = {'id': myOwnID, 'ip': myOwnIP, 'port': myOwnPort, 'file': file_to_leech_name, 'pieces': csn}
    response = requests.get(url=trackerAddress, params=payload, stream=True)

    # # To get the sender and receiver addresses of get request we can use lines below :
    # # Note : get request should be stream type!
    # getReqSocket = socket.fromfd(response.raw.fileno(), socket.AF_INET, socket.SOCK_STREAM)
    # print("GetRequest receiver address : ", getReqSocket.getpeername())
    # print("GetRequest sender address : ", getReqSocket.getsockname())

    print("Update peers list from tracker.")
    logger(myOwnID, "UP___DATA", "Leecher will update its own database of peers list.")
    response = response.json()
    req_interval_time = response['req_interval_time']
    if len(response['peers']) > 1:
        # Refresh the pieces list
        every_body_pieces.clear()
        # List is not empty. But we don't want to connect ourself or
        # those who we have a connection with them already. Let's do
        # something about it. First of all, let's read our peers DB :

        for peer in response['peers']:
            # append pieces of every peer to the list
            every_body_pieces.append(peer['pieces'])
        # sort by frequency from rare to common with our defined function "sort_and_clean"
        # Why clean? It's remove the duplicates too! :)
        # "if it looks good, we look good!" quote by Vidal Sassoon
        pieces_sorted = sort_and_clean(every_body_pieces)
        # we have some pieces :
        csn_sorted = sort_and_clean([csn])
        # what pieces we should request for? list_to_take!
        # It doesn't has any of our pieces. let's remove them
        list_to_take = [item for item in pieces_sorted if item not in csn_sorted]

        connected_ps = pd.read_csv(csvFileName, delimiter=',')
        for peer in response['peers']:
            # searching
            search_ip = connected_ps[connected_ps["dest_ip"].isin([peer['ip']])]
            search_port = connected_ps[connected_ps["dest_port"].isin([peer['port']])]
            # check to avoid attempting to connect again
            if search_ip.shape[0] == 0 and search_port.shape[0] == 0:
                # check to avoid attempting to connect ourself :)
                if str(peer['id']) != myOwnID:
                    # New PPP connection
                    logger(myOwnID, "NEW__PEER", "Get piece ")  # + str(piece) + " from " + str(peer['id']) + " .")
                    print("Connecting to get piece number ")  # , str(piece), " from ", (peer['ip'], peer['port']))
                    # Starting the connection
                    i_thread = threading.Thread(target=LeechMode, args=(peer['ip'], peer['port'], list_to_take))
                    i_thread.daemon = True
                    i_thread.start()
                    # Let's save the connection on our temporary database
                    new_connected_peer = np.array([[myOwnPort, str(peer['id']), peer['ip'], peer['port']]])
                    connected_ps = connected_ps.append(
                        pd.DataFrame(new_connected_peer, columns=['my_port', 'dest_id', 'dest_ip', 'dest_port']))
                    connected_ps.to_csv(csvFileName, index=False)
    # After each interval time we start the thread again to update our DB.
    threading.Timer(req_interval_time, request_tracker).start()


# ######################################
# TODO  :   Procedure   : Starting PEER
# ######################################
os.system('cls||clear')

# Files to transfer between peers
# files are on "files/" subdirectory of project
root, dirs, file_name = next(walk('files'))

# Define hypothetical indexer
# We don't have an indexer in this project.
# But we will use a csv file as its database
indexer_DB_name = '_indexer_seeds.csv'
if not os.path.isfile(indexer_DB_name):
    # # Create indexer seeds database if not exist
    # ########### Indexer DB ################
    # # file_number | file_name | seeder_id #
    # #######################################
    init_inx = {'number': [], 'file_name': [], 'primary_seeder': []}
    inx_db = pd.DataFrame(init_inx)
    inx_db = inx_db.fillna(0)  # with 0s rather than NaNs
    inx_db.to_csv(indexer_DB_name, index=False)

# Defining peer identity
myOwnIP = '127.' + str(randint(2, 254)) + '.' + str(randint(2, 254)) + '.' + str(randint(2, 254))
myOwnPort = randint(6881, 6889)
myOwnID = str(round(time.time()*1000))  # [::-1] # the commented section will use for reversing the string

# Each peer has its own seeds DB. Peer keeps its pieces there.
# Seeder wants this file to keep data to send
# Leecher wants this file to keep received data
# Let's create it!
# ########### PEER seeds DB #################
# # number | file_name | piece | piece_hash #
# ###########################################
peer_seeds_DB = myOwnID + "_seeds.csv"
init_seeds = {'number': [], 'file_name': [], 'piece': [], 'piece_hash': []}
seeds_db = pd.DataFrame(init_seeds)
seeds_db = seeds_db.fillna(0)  # with 0s rather than NaNs
seeds_db.to_csv(peer_seeds_DB, index=False)

# Defining chunk
kilobytes = 1024
megabytes = 1024 * kilobytes
CHUNK_SIZE = 20 * kilobytes  # 20 KB

# buffer size
BUFFER_SIZE = 1024

# msg encoding
FORMAT = "utf-8"

# Interactions with indexer.
# This section will be used to fill indexer place!
leecher = True  # We suppose that peer is leecher except if it's a seeder!
file_to_leech = 0  # If each file has a number, We consider 0 as no specific file
logger(myOwnID, "CONN_INDX", "A hypothetical connection with indexer established.")
p_type = input('Indexer : What are you? ( Just enter its number )\n[1] seeder\n[2] leecher\n')
if int(p_type) == 1:
    os.system('cls||clear')
    msg = 'Indexer : Ok seeder. Send me your torrent file! ( Just enter its number )\n'
    for i in range(len(file_name)):
        msg = msg + '[' + str(i+1) + '] ' + file_name[i] + '\n'
    file = input(msg)
    # Reading indexer DB for torrent of file. If exist peer cant be seeder!
    inx_db = pd.read_csv(indexer_DB_name, delimiter=',')
    # We search for file in indexer seed list to see if it is exist or not?
    search = inx_db[inx_db["file_name"].isin([file_name[int(file)-1]])]
    if search.shape[0] == 0:
        # # First attempt to seed this file!
        # Add this attempt to indexer DB
        new_file = np.array([[file, file_name[int(file)-1], myOwnID]])
        inx_db = inx_db.append(pd.DataFrame(new_file, columns=['number', 'file_name', 'primary_seeder']))
        inx_db.to_csv(indexer_DB_name, index=False)
        # Indexer will send this peer infos for tracker and
        # tracker will save its identity in its DB.
        # So we should add seeder data to tracker DB.
        # There is a new peer connecting, so we append itself to list!
        file_stat = os.stat('files/' + file_name[int(file) - 1])
        file_size = file_stat.st_size
        piece_count = -(-file_size // CHUNK_SIZE)  # c++ : ceil(3.6/2) = 2 -> python : -(-3.6//2) = 2
        pieces = '{'
        for i in range(piece_count):
            pieces = pieces + str(i+1) + ','
        pieces = pieces[:-1] + '}'
        tracker_list = pd.read_csv('_tracker.csv', delimiter=',')
        new_seeder = np.array([[file_name[int(file)-1], myOwnID, myOwnIP, myOwnPort, pieces]])
        tracker_list = \
            tracker_list.append(pd.DataFrame(new_seeder, columns=['file_name', 'p_id', 'p_ip', 'p_port', 'pieces']))
        tracker_list.to_csv('_tracker.csv', index=False)
        # then store the chunks in seeds DB of seeder and create .torrent file of it
        file_number = 1
        with open('files/' + file_name[int(file) - 1], 'rb') as f:
            sha1 = hashlib.sha1()
            SHA1_str = '{'
            chunk = f.read(CHUNK_SIZE)
            seeds_db = pd.read_csv(peer_seeds_DB, delimiter=',')
            while chunk:
                if not chunk:
                    break
                base64_chunk = base64.b64encode(chunk)

                sha1.update(base64_chunk)
                SHA1_str = SHA1_str + sha1.hexdigest() + ','
                # base64_message = base64_bytes.decode('ascii')
                # Add chunk in !
                new_seed = np.array([[file_number, file_name[int(file) - 1], base64_chunk, sha1.hexdigest()]])
                seeds_db = \
                    seeds_db.append(pd.DataFrame(new_seed, columns=['number', 'file_name', 'piece', 'piece_hash']))
                seeds_db.to_csv(peer_seeds_DB, index=False)
                # # We can also create chunked files using below lines :
                # with open(file_name[int(file)-1]+'_' + str(file_number), 'wb') as chunk_file:
                #     chunk_file.write(chunk)
                # Next Chunk
                file_number += 1
                chunk = f.read(CHUNK_SIZE)
            SHA1_str = SHA1_str[:-1]  # remove last character (last comma)
            SHA1_str = SHA1_str + ' }'
        torrentFile = open(file_name[int(file) - 1] + ".torrent", "w")
        # Indexer will give the tracker address to seeder
        trackerAddress = "127.0.0.1:5372"
        metaInfo = \
            '{"announce":"' + trackerAddress + '", "info":{ "length":' + str(file_size) + \
            ',"name":"' + file_name[int(file) - 1] + '","piece length":' + str(CHUNK_SIZE) + \
            ', "pieces":"' + SHA1_str + '" } } '
        # metaInfo = bencodepy.encode(
        #     {
        #         'announce': trackerAddress,
        #         'info':
        #             {
        #                 'length': str(file_size),
        #                 'name': file_name[int(file) - 1],
        #                 'piece length': str(CHUNK_SIZE),
        #                 'pieces': SHA1_str
        #             }
        #     })
        torrentFile.write(metaInfo)
        torrentFile.close()
        os.system('cls||clear')
        print('Peer : torrent file sent to indexer!')
        logger(myOwnID, "TORR_SENT", "torrent of " + file_name[int(file) - 1] + " sent to indexer.")
        leecher = False
    else:
        os.system('cls||clear')
        decision = input('We have it file on our swarms! Do you want to...?\n[1] Leech it\nor\n[0] Cancel operation\n')
        if int(decision) == 0:
            logger(myOwnID, "PEER_ABRT", "Peer will abort the operation.")
            sys.exit(0)
        else:
            file_to_leech = int(file)
# Now the seeder going to server mode, waiting for requests
# But leechers will connect to tracker for seeder addresses
if leecher:
    # Leecher section
    os.system('cls||clear')
    if file_to_leech == 0:
        msg = 'Indexer : Ok leecher, search your file! ( Just enter its number )\n'
        for i in range(len(file_name)):
            msg = msg + '[' + str(i + 1) + '] ' + file_name[i] + '\n'
        file_to_leech = input(msg)
        os.system('cls||clear')
        file_to_leech_name = file_name[int(file_to_leech) - 1]
        # Reading indexer DB for torrent of file. If exist peer cant be seeder!
        inx_db = pd.read_csv(indexer_DB_name, delimiter=',')
        # We search for file in indexer seed list to see if it is exist or not?
        search = inx_db[inx_db["file_name"].isin([file_to_leech_name])]
        if search.shape[0] == 0:
            os.system('cls||clear')
            print('This file is not seeded yet! Ending Operation...')
            logger(myOwnID, "NOT__LICH", "The file to leech is not seeded yet! Ending Operation!")
            logger(myOwnID, "PEER_ABRT", "Peer will abort the operation.")
            sys.exit(0)
    else:
        file_to_leech_name = file_name[int(file_to_leech) - 1]

    # We want to have a list of every body pieces and update it with every response from tracker
    every_body_pieces = []
    list_to_take = []
    # what is our pieces? current seeds numbers = csn
    csn = ''
    logger(myOwnID, "GOT__TORR", "Peer got the torrent file from indexer and now connecting to tracker.")
    with open(file_to_leech_name + ".torrent", "r") as torrentFile:
        mInfo = torrentFile.read()
        Dictionary = json.loads(mInfo)
    # print(Dictionary['info']['name']) # will print fileName.ext
    announce = Dictionary['announce'].split(":")
    serverIP = announce[0]  # "127.0.0.1"
    serverPort = announce[1]  # "5372"
    trackerAddress = "http://" + serverIP + ":" + serverPort
    # Start tracking of others by the use of tracker server
    data = {'my_port': [], 'dest_id': [], 'dest_ip': [], 'dest_port': []}
    csvFileName = myOwnID + "_PPP_list.csv"
    df = pd.DataFrame(data)
    df = df.fillna(0)  # with 0s rather than NaNs
    df.to_csv(csvFileName, index=False)
    request_tracker()

while True:
    try:
        print('Waiting for requests.')
        logger(myOwnID, "WAIT__REQ", "Seeder waits for requests for files.")
        # we are going to seeding mode simultaneously
        SeedMode()
    except KeyboardInterrupt:
        sys.exit(0)
