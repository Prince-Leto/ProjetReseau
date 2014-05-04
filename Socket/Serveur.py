import socket, select

LIST = []
FILES = {}
BUFFER = 4096
PORT = 5003
TEXT = [['Test', '']]

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# serveur.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
serveur.bind(("", PORT))
serveur.listen(10)

LIST.append(serveur)

print("Serveur started on port " + str(PORT))

def BroadCast(sock, message):
	for socket in LIST:
		if socket != serveur and socket != sock and FILES[sock][0] == FILES[socket][0] and FILES[socket][0] != -1:
			try:
				socket.send(message)
			except:
				print("Client disconnected")
				socket.close()
				LIST.remove(socket)

def RemoteFiles(sock):
	m = 'f'
	if len(TEXT) > 0:
		for f in range(len(TEXT) - 1):
			m += TEXT[f][0] + ","
		m += TEXT[len(TEXT) - 1][0]
	sock.send(m.encode("utf-8"))

while 1:
	read, write, errors = select.select(LIST, [], [])

	for sock in read:
		if sock == serveur:
			sockc, addr = serveur.accept()
			# sockc.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			LIST.append(sockc)
			FILES[sockc] = [-1, addr]
			print("Client (%s, %s) connected" % addr)
			RemoteFiles(sockc)
		else:
			try:
				data = sock.recv(BUFFER)
				data = data.decode("utf-8")
				print(data)
				size = int(data[0:4])
				data = data[4:4 + size]
				if data == "GetFiles":
					RemoteFiles(sock)
				elif data[0:1] == "f":
					FILES[sock][0] = int(data[1:])
					sock.send(("n0," + TEXT[FILES[sock][0]][1]).encode("utf-8"))
				elif data[0:1] == "c":
					TEXT.append([data[1:], ""])
				elif data[0:1] == "k":
					data = data[0:1] + str(FILES[sock][1][1]) + ":" + data[1:]
					BroadCast(sock, data.encode("utf-8"))
				elif data:
					BroadCast(sock, data.encode("utf-8"))
					if data[0:1] == "i":
						TEXT[FILES[sock][0]][1] = TEXT[FILES[sock][0]][1][:int(data[1:].split(",", 1)[0])] + data[1:].split(",", 1)[1] + TEXT[FILES[sock][0]][1][int(data[1:].split(",", 1)[0]):]
					elif data[0:1] == "d":
						TEXT[FILES[sock][0]][1] = TEXT[FILES[sock][0]][1][:int(data[1:].split(",", 1)[0])] + TEXT[FILES[sock][0]][1][int(data[1:].split(",", 1)[1]):]

			except:
				print('Client disconnected')
				sock.close()
				LIST.remove(sock)

serveur.close()