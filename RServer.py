import threading
import socket
import json
import sys

#currently using normal dict.
#TBD: port to database
class RendezvousServer:

	def __init__(self, port):
		self.serv_port = port
		self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serv_sock.bind(("0.0.0.0", self.serv_port))
		self.peer_table = dict()

	def respondToQuery(self, peer_sock):
		"""
		Read a query from the peer socket and respond appropriately
		Query Format:
		{"username": "<username>", "local_ip": "<local_ip>", "local_port": "<listening_port>", "query": "<ALL>/<target_username>"}
		"""
		query_dict = json.loads(peer_sock.recv(1024))
		self.peer_table[query_dict['username']] = (query_dict["local_ip"], query_dict["local_port"])
		if query_dict["query"] == "ALL":
			resp_json = json.dumps(self.peer_table)
		elif query_dict["query"]:
			if self.peer_table.has_key(query_dict["query"]):
				resp_dict = {query_dict["query"]: self.peer_table[query_dict("query")]}
				print resp_dict
				resp_json = json.dumps(resp_dict)
			else:
				resp_json = json.dumps(dict())
		peer_sock.send(resp_json)
		peer_sock.close()

	def runServer(self):
		print "Server initialized."
		self.serv_sock.listen(100)
		print "Server running on port " + str(self.serv_port) + "...."
		while True:
			conn, addr = self.serv_sock.accept()
			print "Peer at " + str(addr) + " connected..."
			threading.Thread(target=self.respondToQuery, args=(conn,)).start()

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
	RendezvousServer(int(sys.argv[1])).runServer()
