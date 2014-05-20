import socket, select, sys, os

LIST = []
BUFFER = 4096
PORT = 5000

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serveur.bind(("", PORT))
serveur.listen(10)

LIST.append(serveur)

print("Serveur started on port " + str(PORT))

while True:
	read, write, errors = select.select(LIST, [], [])

	for sock in read:
		if sock == serveur:
			sockc, addr = serveur.accept()
			LIST.append(sockc)
			print("Client (%s, %s) connected" % addr)

		else:
			try:
				data = sock.recv(BUFFER)
				data = data.decode('utf-8')
				print(data.split(chr(0)))

			except:
				print('Client disconnected')
				sock.close()
				LIST.remove(sock)

serveur.close()