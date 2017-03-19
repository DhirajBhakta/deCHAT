# Test comment
import socket
import os
import sys
import time
import threading
import json

class Peer:
	"""
	recv_sock	:	Listens for messages.
				  	The peer binds to his recv_sock. and the recv_sock binds to the host's own (IP,port),the port being the listening port.
				  	[Note the clear difference between sending port and listening port]
				  	So , if any outsider wants to send msg to this peer, he(outsider) sends the msg to recv_sock of this peer.
				  	Hence, recieving messages from random peers is done in a separate Thread.

	send_sock	:	messages are SENT through send_sock
				  	But "WHOM" to send, must be specified.
				  	So the peer types "dhiraj:this is my msg" .Then, itll be parsed.,The destination is identified via a table.
					..and the msg "this is my msg" is sent to "dhiraj"'s (IP,PORT)..i.e recv_sock of dhiraj'
					So,this peer's input (i.e a message intended to any other specified peer , or an END command) is parsed
					continuously in a separate thread.

	getAllConnectedPeerDetails():
					 This function contacts the Rendezvous Server, and supplies its own (IP,PORT) to be registered.
				 	The R.Server then returns a dict of all registered peers.
				 	>>>T.B.D : call this function regularly periodically , to keep track of all connected peers
	"""
	def __init__(self,R_Server_addr,username, self_port):
		self.username 	   = username
		self.R_Server_addr = R_Server_addr   #Rendezvous Server address i.e('IP',port) tuple
		self.my_local_ip   = "127.0.0.1"
		self.my_local_port = self_port  #listening port
		self.peer_table = {}
		self.getAllConnectedPeerDetails()

		self.sentinel = True #Threads check on sentinel to stop/continue        
		self.recv_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.recv_sock.bind((self.my_local_ip, self.my_local_port)) #recv_sock bound to the listening port.

		self.send_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

		self.msg_recv_thread = threading.Thread(target=self.recieveMessages)
		self.msg_recv_thread.start()

		self.msg_send_thread = threading.Thread(target=self.sendMessages)
		self.msg_send_thread.start()



	#only to receive
	#special messages recieved:
	#	data['MSG'] = "DEL" ---> the sender wants to leave the network, and is asking every peer to remove his data
	#							 from their peer_table 
	#
	#   data['MSG'] = "FILE"--> the sender is about to send a file ,

	def recieveMessages(self):
		while(self.sentinel):
			data,sender_addr = self.recv_sock.recvfrom(1024)
			data = json.loads(data)
			#request to delete sender's entry from peer_table
			if (data['MSG']=="DEL"):
				self.peer_table.pop(data['USERNAME'],None)
				continue
			#normal text message
			if not self.peer_table.has_key(data['USERNAME']):
				self.peer_table[data['USERNAME']] = (sender_addr[0],data['PORT']) 
				#note that here ^^^ I didnt use sender_addr[1] as the port, but instead, used the port supplied by the sender
				#					himself in the body of the message. This is because, peer_table keeps track of listening ports
				#					of other peers. sender_addr[1] gives the sending port of the sender. Since there's no possible way
				#					to derive the sender's listening port, he intentionally packs that info in the message.
			#pretty-print here,.
			print "INCOMING MESSAGE >"+data['USERNAME'] +":"+data['MSG']


	#only to Parse input,
	#and send
	def sendMessages(self):
		while(self.sentinel):
			user_input = raw_input()
			if (user_input =="EXIT"):
				self.sentinel = False
				DEL_signal = dict(MSG="DEL",PORT=self.my_local_port,USERNAME=self.username)
				# the quitting peer packs his listening port in the message.  
				for reciever in self.peer_table.values():
					self.send_sock.sendto(json.dumps(DEL_signal),reciever)
				self.send_sock.close()
				self.recv_sock.close()
				print "Connection Closed.....\n\n"
				break
			elif(user_input =="SHOW_USERS"):
				print "\n\nThere are "+str(len(self.peer_table))+" connected usernames:"
				for uname in self.peer_table.keys():
					print "-- "+uname
				print "------------------------------"
				continue

			elif(user_input =="HELP"):
				print "\n\n\n----------WELCOME TO DECENTRALIZED CHAT v1.0-----------"
				print "SHOW_USERS: full listing of connected peers."
				print "HELP      : Show this help."
				print "EXIT      : Quit chatting."
				print "------------------------------------------------------\n\n\n"
				continue
			try:
				reciever_username,msg = user_input.strip().split(':')
				data= dict(MSG=msg,PORT=self.my_local_port,USERNAME=self.username)
			except Exception as e:
				print "\nWARNING!:Messages are of the form : <USERNAME>:<MESSAGE>\n"
				continue

			if(self.peer_table.has_key(reciever_username)):
				self.send_sock.sendto(json.dumps(data),self.peer_table[reciever_username])
			else:
				print "\n!!!ERROR: "+recieverID+" could not be resolved!"
				print "type HELP for more info.\n"



	def getAllConnectedPeerDetails(self):
	
		

	#First, register yourself with the R.Server,
	# ...send your own IP,port (private,obviously..as public IP,port can be extracted from IP header)
	# ...youre sending your listening port,
	#Note:TCP connection with RServer
		temp_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		connected = False
		NOT_CONN_MSG = False
		while(not connected):
			try:
				time.sleep(1)
				temp_sock.connect(self.R_Server_addr)
				print "connected"
				break		
			except Exception as e:
				if not NOT_CONN_MSG:
					sys.stderr.write("R.Server down. Attempting again.")
					NOT_CONN_MSG = True
				else:
					sys.stderr.write(" .")
				
		
		self_info = dict(USERNAME=self.username, LOCALIP=self.my_local_ip, LOCALPORT=self.my_local_port, QUERY="ALL")
		temp_sock.send(json.dumps(self_info))
		#now get a dict of all peers,addr
		self.peer_table = json.loads(temp_sock.recv(1024*10))
		for username in self.peer_table.keys():
			self.peer_table[username] = tuple(self.peer_table[username])
		temp_sock.close()






#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------






#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------




if __name__ == '__main__':
	if (len(sys.argv)<4):
		print "USAGE: "+ sys.argv[0] +" <R.Server IP:port> <username> <self-PortNumber>"
		sys.exit()
	#Rendezvous Server (IP,port) parsing.
	R_Server_addr = sys.argv[1].split(':')
	R_Server_addr[1] = int(R_Server_addr[1])
	R_Server_addr = tuple(R_Server_addr)
	selfPort = int(sys.argv[3])
	username = sys.argv[2]



	peer = Peer(R_Server_addr, username, selfPort)
