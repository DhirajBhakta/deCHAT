import socket
import json


#currently using normal dict.
#TBD: port to database
import sys

def runServer(port):
	peers = dict()
	servSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	servSock.bind(('0.0.0.0',port))
	servSock.listen(100)
	print("Server running on port " + str(port))
	while(True):
		conn,addr = servSock.accept()
		data = json.loads(conn.recv(1024))
		username = data['USERNAME']
		if not peers.has_key(username):
			ip = str(data['IP'])
			port = int(data['PORT'])
			peers[username] = (ip,port)
			print(peers)
		conn.send(json.dumps(peers))
		conn.close()


if __name__ == "__main__":
	print("Attempting to initialize server...")
	runServer(int(sys.argv[1]))
