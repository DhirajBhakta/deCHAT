import socket
import os
import sys
import threading
import json

class Peer:
	#recvSock :   Listens for messages.
	#			  The peer binds to his recvSock. and the recvSock binds to the host's own (IP,port)
	#			  So , if any outsider wants to send msg to this peer, he(outsider) sends the msg to recvSock of this peer.
	#			  Hence, recieving messages from random peers is done in a separate Thread.

	#sendSock :   messages are SENT through sendSock
	#			  But "WHOM" to send, must be specified.
	#			  So the peer types "dhiraj:this is my msg" .Then, itll be parsed.,The destination is identified via a table.
	#				..and the msg "this is my msg" is sent to "dhiraj"'s (IP,PORT)..i.e recvSock of dhiraj'
	#	So,this peer's input (i.e a message intended to any other specified peer , or an END command) is parsed continuously in a
	#	separate thread.

	#getAllConnectedPeerDetails():   
	#			 This function contacts the Rendezvous Server, and supplies its own (IP,PORT) to be registered.
	#			 The R.Server then returns a dict of all registered peers.
	#			 >>>T.B.D : call this function regularly periodically , to keep track of all connected peers
	
	def __init__(self,R_Server_addr,username, self_port):
		self.username 	   = username
		self.R_Server_addr = R_Server_addr   #Rendezvous Server address i.e('IP',port) tuple
		self.my_local_ip   = os.popen('ifconfig wlan0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1').read().strip()
		self.my_local_port = self_port  #listening port
		self.peerMap = {}
		self.getAllConnectedPeerDetails()
		
		self.sentinel = True
		self.recvSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.recvSock.bind((self.my_local_ip, self.my_local_port))
		
		self.sendSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

		self.msg_recv_thread = threading.Thread(target=self.recieveMessages)
		self.msg_recv_thread.start()

		self.msg_send_thread = threading.Thread(target=self.sendMessages)
		self.msg_send_thread.start()
		
	

	#only to receive
	def recieveMessages(self):
		print "now listening for msgs..."
		while(self.sentinel):
			data,remoteAddr = self.recvSock.recvfrom(1024)
			data = json.loads(data)
			if (data['MSG']=="DEL"):
				self.peerMap.pop(data['USERNAME'],None)
				continue
			if not self.peerMap.has_key(data['USERNAME']):
				self.peerMap[data['USERNAME']] = (remoteAddr[0],data['PORT'])
			#pretty-print here,.	
			print "------- "+data['USERNAME'] +" says :"+data['MSG']+"\n"


	#only to Parse input,
	#and send 
	def sendMessages(self):
		print "now waiting for user input..."
		while(self.sentinel):
			user_input = raw_input()
			if (user_input =="EXIT"):
				self.sentinel = False
				DEL_signal = dict(MSG="DEL",PORT=self.my_local_port,USERNAME=self.username)
				for reciever in self.peerMap.values():
					self.sendSock.sendto(json.dumps(DEL_signal),reciever)
				self.sendSock.close()
				self.recvSock.close()
				print "Connection Closed.....\n\n"
				break
			elif(user_input =="SHOW_USERS"):
				print "There are "+str(len(self.peerMap))+" connected usernames:-------------"
				for uname in self.peerMap.keys():
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
				recieverID,msg = user_input.strip().split(':')
				dataToSend = dict(MSG=msg,PORT=self.my_local_port,USERNAME=self.username)
			except Exception as e:
				print "WARNING!:Messages are of the form : <USERNAME>:<MESSAGE>"
				continue
			
			if(self.peerMap.has_key(recieverID)):
				self.sendSock.sendto(json.dumps(dataToSend),self.peerMap[recieverID])
			else:
				print "!!!ERROR: "+recieverID+" could not be resolved!"
				print "type HELP for more info."
				


	def getAllConnectedPeerDetails(self):
	#First, register yourself with the R.Server,
	# ...send your own IP,port (private,obviously..as public IP,port can be extracted from IP header)
		tempSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		tempSock.connect(self.R_Server_addr)

		PeerInfo = dict(USERNAME=self.username,IP=self.my_local_ip,PORT=self.my_local_port)
		tempSock.send(json.dumps(PeerInfo))
		#now get a dict of all peers,addr 
		self.peerMap = json.loads(tempSock.recv(1024*100))
		for key in self.peerMap.keys():
			self.peerMap[key] = tuple(self.peerMap[key])
		tempSock.close()


			



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
