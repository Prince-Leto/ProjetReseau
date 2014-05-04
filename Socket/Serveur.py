import socket, select, sys

LIST = []
FILES = {}
BUFFER = 4096
PORT = 5000
TEXT = [['Test', '']]

if(len(sys.argv) < 2) :
	print('Usage : python3 Serveur.py port')
	sys.exit()

PORT = int(sys.argv[1])

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# serveur.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
serveur.bind(("", PORT))
serveur.listen(10)

LIST.append(serveur)

print("Serveur started on port " + str(PORT))

def PrepareSending(message):
	l = len(message)
	m = str(l)
	if l < 10000:
		for i in range(1,4):
			if l < 10**i:
				m = "0" + m
	else:
		sys.stdout.write("Inserting too much text. Please reload the file.")
	return (m + message).encode("utf-8")

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
	sock.send(PrepareSending(m))

def SeparateData(param):
	m = []
	while len(param) > 0:
		m.append(param[4:4 + int(param[0:4])])
		param = param[4 + int(param[0:4]):]
	return m

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
				for data in SeparateData(data):
					if data == "GetFiles":
						RemoteFiles(sock)
					elif data[0:1] == "f":
						FILES[sock][0] = int(data[1:])
						sock.send(PrepareSending("n0," + TEXT[FILES[sock][0]][1]))
					elif data[0:1] == "c":
						TEXT.append([data[1:], ""])
					elif data[0:1] == "k":
						data = data[0:1] + str(FILES[sock][1][1]) + ":" + data[1:]
						BroadCast(sock, PrepareSending(data))
					elif data:
						BroadCast(sock, PrepareSending(data))
						if data[0:1] == "i":
							TEXT[FILES[sock][0]][1] = TEXT[FILES[sock][0]][1][:int(data[1:].split(",", 1)[0])] + data[1:].split(",", 1)[1] + TEXT[FILES[sock][0]][1][int(data[1:].split(",", 1)[0]):]
						elif data[0:1] == "d":
							TEXT[FILES[sock][0]][1] = TEXT[FILES[sock][0]][1][:int(data[1:].split(",", 1)[0])] + TEXT[FILES[sock][0]][1][int(data[1:].split(",", 1)[1]):]

			except:
				print('Client disconnected')
				sock.close()
				LIST.remove(sock)

serveur.close()