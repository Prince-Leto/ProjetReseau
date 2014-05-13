import socket, select, sys, os

# LIST est la liste des sockets dont le socket server
LIST = []
# FILES  est un tableau associatif des sockets et des fichiers
FILES = {}
# BUFFER
BUFFER = 4096
# PORT par défaut
PORT = 5000
# TEXT est l'ensemble des fichiers stockés par le serveur accecible par l'utilisateur   
TEXT = []
# MAX_MODIF est le nombre de char entre chaque sauvegarde automatique
MAX_MODIF = 10


# LookFiles regarde si le dossier "LISSData" existe sur le serveur sinon il le crée.
# 	et importe dans TEXT l'ensemble des fichiers présents dans "LISSData" sous la forme 
#	[le nom du fichier, le texte contenu dans le fichier, le nombre de modifications]
def LookFiles():
	global TEXT
	try: 
		for f in os.listdir('LISSData'):
			if os.path.isfile(os.path.join('LISSData', f)):
				rf = open(os.path.join('LISSData', f), 'r')
				t = rf.read()
				rf.close()
				TEXT.append([f, t, 0])
	except:
		os.mkdir('LISSData')

# Lancement de la fonction LookFiles
LookFiles()

# Write File remplace le contenu du fichier d'indice i par l'ensemble du text contenu dans TEXT 
def WriteFile(i):
	global TEXT
	f=open (os.path.join('LISSData', TEXT[i][0]), 'w')
	f.write(TEXT[i][1])
	f.close()

# Vérification du nombre d'arguments
if(len(sys.argv) < 2) :
	print('Usage : python3 Serveur.py port')
	sys.exit()

# définit le port associé au serveur
PORT = int(sys.argv[1])

# initialisation des sockets
serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# serveur.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
serveur.bind(("", PORT))
serveur.listen(10)

# ajoute le serveur à la liste des sockets
LIST.append(serveur)

# affichage en console du démarrage du serveur
print("Serveur started on port " + str(PORT))

# PrepareSending formate le message avec le nombre de charactère devant.
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

# BroadCast renvoie le message à l'ensemble des clients sauf à celui dont elle provient (donc on exclu aussi le serveur)
def BroadCast(sock, message):
	for socket in LIST:
		if socket != serveur and socket != sock and FILES[sock][0] == FILES[socket][0] and FILES[socket][0] != -1:
			try:
				socket.send(message)
			except:
				print("Client disconnected")
				socket.close()
				LIST.remove(socket)

# RemoteFiles renvoie à l'utilisateur la liste des fichiers
def RemoteFiles(sock):
	m = 'f'
	if len(TEXT) > 0:
		for f in range(len(TEXT) - 1):
			m += TEXT[f][0] + ","
		m += TEXT[len(TEXT) - 1][0]
	sock.send(PrepareSending(m))

# SeparateData sépare les informations de manière logique, soit taille(0000-9999)+données
def SeparateData(param):
	m = []
	while len(param) > 0:
		m.append(param[4:4 + int(param[0:4])])
		param = param[4 + int(param[0:4]):]
	return m

# On lance la boucle infini 
while 1:
	read, write, errors = select.select(LIST, [], [])

	# pour chaque socket lu dans la LIST
	for sock in read:
		# Si cette socket est celle du serveur alors il y a une nouvelle connection donc on l'accepte
		if sock == serveur:
			sockc, addr = serveur.accept()
			# sockc.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			LIST.append(sockc)
			FILES[sockc] = [-1, addr]
			print("Client (%s, %s) connected" % addr)
			RemoteFiles(sockc)

		# Sinon on traite la socket du client et on effectu l'action associé
		else:
			try:
				data = sock.recv(BUFFER)
				data = data.decode("utf-8")
				for data in SeparateData(data):
					# Si demande l'accès au fichier on lui revoie la liste
					if data == "GetFiles":
						RemoteFiles(sock)
					# Si il demande l'accès à un fichier alors on lui envoie son contenu
					elif data[0:1] == "f":
						FILES[sock][0] = int(data[1:])
						sock.send(PrepareSending("n0," + TEXT[FILES[sock][0]][1]))
					# Si il demande de créer un fichier on le crée
					elif data[0:1] == "c":
						TEXT.append([data[1:], ""])
						RemoteFiles(sock)
					# Ajout le numéro de la socket au message et broadcast, La position du curseur
					elif data[0:1] == "k":
						data = data[0:1] + str(FILES[sock][1][1]) + ":" + data[1:]
						BroadCast(sock, PrepareSending(data))
					# Sinon ajout et suppression des charactères 
					elif data:
						BroadCast(sock, PrepareSending(data))
						if data[0:1] == "i":
							TEXT[FILES[sock][0]][2] += 1
							TEXT[FILES[sock][0]][1] = TEXT[FILES[sock][0]][1][:int(data[1:].split(",", 1)[0])] + data[1:].split(",", 1)[1] + TEXT[FILES[sock][0]][1][int(data[1:].split(",", 1)[0]):]
						elif data[0:1] == "d":
							TEXT[FILES[sock][0]][2] += 1
							TEXT[FILES[sock][0]][1] = TEXT[FILES[sock][0]][1][:int(data[1:].split(",", 1)[0])] + TEXT[FILES[sock][0]][1][int(data[1:].split(",", 1)[1]):]
						if TEXT[FILES[sock][0]][2] >= MAX_MODIF:
							TEXT[FILES[sock][0]][2] = 0
							WriteFile(FILES[sock][0])
			# Sinon c'est que le client est déconnecté et on l'affiche. Deplus, on supprime sa socket associé.
			except:
				print('Client disconnected')
				sock.close()
				LIST.remove(sock)

serveur.close()