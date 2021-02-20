# ######################################
# TODO  :   SOROOSH NOORZAD - 99205372
# ######################################

# ######################################
# TODO  :   Import libraries
# ######################################
import os
import json
import threading
import numpy as np
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer

# maybe we can remove below libraries from here.
# IDK. should we?
import datetime
import urllib.parse as url_parse
from urllib.parse import parse_qs


# ######################################
# TODO  :   Classes and functions
# ######################################
from functions import logger


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/404":
            # Just for fun and testing :)
            # 404 means not found
            self.send_error(404)
        else:
            url = url_parse.urlparse(self.path)
            parsed = parse_qs(url.query)
            rec_id = int(parsed["id"][0])
            rec_ip = parsed["ip"][0]
            rec_port = parsed["port"][0]
            rec_file = parsed["file"][0]
            rec_pieces = parsed["pieces"][0]
            logger(TRACKER, 'TRAK___REQ', 'Tracker got a new request from ' + rec_ip + ":" + rec_port + " .")
            # 200 means OK
            self.send_response(200)
            # It's preferable for us to use application/json. It's more standard than text/plain content-type.
            # But it makes almost no performance difference.
            self.send_header('Content-type', 'application/json')
            # We could set some other headers and in future maybe we implemented some! who knows?
            self.end_headers()
            # Reading trackers DB and preparing right response for GET request.
            peers = pd.read_csv(TRACKER + '.csv', delimiter=',')
            # We search for GET sender to see if it is asking us for the first time or what?
            search = peers[peers["p_id"].isin([rec_id])]
            if search.shape[0] == 0:
                # There is a new peer connecting, so we append itself to list!
                new_peer = np.array([[rec_file, rec_id, rec_ip, rec_port, rec_pieces]])
                peers = peers.append(pd.DataFrame(new_peer, columns=['file_name', 'p_id', 'p_ip', 'p_port', 'pieces']))
                peers.to_csv(TRACKER + '.csv', index=False)

            # Preallocate of JSON response
            response = {'peers': {}, 'req_interval_time': req_interval_time}
            peers_list = []
            for index, peer in peers.iterrows():
                if peer['file_name'] == rec_file:
                    peers_list.append({
                        'index': index,
                        'fn': peer['file_name'],
                        'id': peer['p_id'],
                        'ip': peer['p_ip'],
                        'port': peer['p_port'],
                        'pieces': peer['pieces']
                    })
            response['peers'] = peers_list
            json_response = json.dumps(response)
            # JSONResponse = Response.to_json(orient ='records')#[1:-1].replace('},{', '} {')

            # json.dumps always outputs a str, wfile.write requires bytes
            # self.wfile.write(json.dumps(JSONResponse).encode(FORMAT))
            self.wfile.write(json_response.encode(FORMAT))


# ######################################
# TODO  :   Procedure
# ######################################
# Trackers identity
# an arbitrary host
serverIP = '127.0.0.1'
# an arbitrary port
serverPort = 5372
# bufferSize
BUFFER_SIZE = 1024
# msg encoding
FORMAT = "utf-8"
# Peer request interval time
req_interval_time = 30
# Tracker prefix for files
TRACKER = '_tracker'
# # Create trackers peer database
# ########### tracker DB #############
# # file_name | p_id | p_ip | p_port #
# ####################################
data = {'file_name': [], 'p_id': [], 'p_ip': [], 'p_port': [], 'pieces': []}
dataframe = pd.DataFrame(data)
dataframe = dataframe.fillna(0)  # with 0s rather than NaNs
dataframe.to_csv(TRACKER + '.csv', index=False)
logger(TRACKER, 'CRTE__TKDB', 'Tracker database has been created.')

if __name__ == "__main__":
    os.system('cls||clear')
    webServer = HTTPServer((serverIP, serverPort), HTTPHandler)
    logger(TRACKER, 'TRAK__SERV', 'Tracker Server started at http://' + serverIP + ":" + str(serverPort))
    print("Server started at http://%s:%s" % (serverIP, serverPort))
    threading.Thread(target=webServer.serve_forever).start()
    # webServer.server_close()
    # webServer.shutdown()
    # print("Server stopped.")
