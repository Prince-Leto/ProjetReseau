import socket, select, sys, os

Sockets = []
Buffer = 4096
Port = 5000

def SeparateData(Data):
	Data = Data[:len(Data) - 1]
	return Data.split(chr(1))

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serveur.bind(("", Port))
serveur.listen(10)

Sockets.append(serveur)

print("Serveur started on port " + str(Port))

while True:
	read, write, errors = select.select(Sockets, [], [])

	for Sock in read:
		if Sock == serveur:
			sockc, addr = serveur.accept()
			Sockets.append(sockc)
			print("Client (%s, %s) connected" % addr)

		else:
			try:
				Data = Sock.recv(Buffer)
				if Data:
					Data = Data.decode('utf-8')
					for Data in SeparateData(Data):
						Size, Data = Data.split('|', 1) # TODO, check size
						Data = Data[:len(Data) - 1]
						print(Data.split(chr(0)))
				else:
					print('Client disconnected')
					Sock.close()
					Sockets.remove(Sock)

			except:
				print('Client disconnected')
				Sock.close()
				Sockets.remove(Sock)

serveur.close()