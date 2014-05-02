import socket, select

def broadCast(sock, message):
	for socket in LIST:
		if socket != serveur and socket != sock:
			try:
				socket.send(message)
			except:
				print("Client disconnected")
				socket.close()
				LIST.remove(socket)

LIST = []
BUFFER = 4096
PORT = 5003
Text = "Empty"

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serveur.bind(("", PORT))
serveur.listen(10)

LIST.append(serveur)

print("Chat serveur started on port " + str(PORT))

while 1:
	read, write, errors = select.select(LIST, [], [])

	for sock in read:
		if sock == serveur:
			sockc, addr = serveur.accept()
			LIST.append(sockc)
			sockc.send(("i0," + Text).encode("utf-8"))
			print("Client (%s, %s) connected" % addr)

		else:
			try:
				data = sock.recv(BUFFER)
				if data:
					broadCast(sock, data)
					data = data.decode("utf-8")
					if data[0:1] == "i":
						Text += data[1:].split(",", 1)[1]
						# Text[int(data[1:].split(",", 1)[0])]
					# elif data[0:1] == "d":
					# 	Text = Text[0:int(data[1:].split(",", 1))[0]] + Text[int(data[1:].split(",", 1))[1]:]
			except:
				print("Client disconnected")
				sock.close()
				LIST.remove(sock)
				continue

serveur.close()