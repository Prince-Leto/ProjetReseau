import socket, select

LIST = []
FILES = {}
BUFFER = 4096
PORT = 5003
TEXT = [['Test', '']]

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serveur.bind(("", PORT))
serveur.listen(10)

LIST.append(serveur)

print("Serveur started on port " + str(PORT))

def BroadCast(sock, message):
	for socket in LIST:
		if socket != serveur and socket != sock and FILES[sock] == FILES[socket] and FILES[socket] != -1:
			try:
				socket.send(message)
			except:
				print("Client disconnected")
				socket.close()
				LIST.remove(socket)

while 1:
	read, write, errors = select.select(LIST, [], [])

	for sock in read:
		if sock == serveur:
			sockc, addr = serveur.accept()
			LIST.append(sockc)
			FILES[sockc] = -1
			print("Client (%s, %s) connected" % addr)
		else:
			try:
				data = sock.recv(BUFFER)
				data = data.decode("utf-8")
				if data == "GetFiles":
					m = 'f'
					if len(TEXT) > 0:
						for f in range(len(TEXT) - 1):
							m += TEXT[f][0] + ","
						m += TEXT[len(TEXT) - 1][0]
					sock.send(m.encode("utf-8"))
				elif data[0:1] == "f":
					FILES[sock] = int(data[1:])
					sock.send(("n0," + TEXT[FILES[sock]][1]).encode("utf-8"))
				elif data[0:1] == "c":
					TEXT.append([data[1:], "Empty"])
					print(TEXT)
				elif data[0:1] == "k":
					BroadCast(sock, data.encode("utf-8"))
				elif data:
					# print(TEXT[FILES[sock]][1][:int(data[1:].split(",", 1)[0])])
					BroadCast(sock, data.encode("utf-8"))
					if data[0:1] == "i":
						TEXT[FILES[sock]][1] = TEXT[FILES[sock]][1][:int(data[1:].split(",", 1)[0])] + data[1:].split(",", 1)[1] + TEXT[FILES[sock]][1][int(data[1:].split(",", 1)[0]):]
					elif data[0:1] == "d":
						TEXT[FILES[sock]][1] = TEXT[FILES[sock]][1][:int(data[1:].split(",", 1)[0])] + TEXT[FILES[sock]][1][int(data[1:].split(",", 1)[1]):]
					print(TEXT[FILES[sock]])

			except:
				print('Client disconnected')
				sock.close()
				LIST.remove(sock)

serveur.close()