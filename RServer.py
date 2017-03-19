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
		self.serv_sock.bind(("127.0.0.1", self.serv_port))
		self.peer_table = dict()

	def respondToQuery(self, peer_sock):
		"""
		Read a query from the peer and respond appropriately
		Query Format:
		{"USERNAME": "<username>", "LOCALIP": "<local_ip>", "LOCALPORT": "<listening_port>", "QUERY": "<ALL>/<target_username>"}
		"""
		query_dict = json.loads(peer_sock.recv(1024))
		if not self.peer_table.has_key(query_dict['USERNAME']):
			self.peer_table[query_dict['USERNAME']] = (query_dict['LOCALIP'], query_dict['LOCALPORT'])
		if query_dict['QUERY'] == 'ALL':
			resp_json = json.dumps(self.peer_table)
		else:#specific target (a peer wants to know addr of a specific peer)
			target_username = query_dict["QUERY"].strip()
			if self.peer_table.has_key(target_username):
				resp_dict = {target_username: self.peer_table[target_username]}
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
			peer_sock, peer_addr = self.serv_sock.accept()
			print "Peer at " + str(peer_addr) + " connected..."
			threading.Thread(target=self.respondToQuery, args=(peer_sock,)).start()





if __name__ == "__main__":
	print("Attempting to initialize server...")
	RendezvousServer(int(sys.argv[1])).runServer()
