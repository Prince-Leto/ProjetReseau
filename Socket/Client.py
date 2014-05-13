import socket, select, sys

# La fonction PrepareSending formate le message avec le nombre de charactère devant
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

# Affiche -> au début de chaque ligne
def prompt() :
	sys.stdout.write('-> ')
	sys.stdout.flush()

# Main en Python
if __name__ == "__main__":

	# Vérification du nombre d'arguments
	if(len(sys.argv) < 3) :
		print('Usage : python3 Client.py hostname port')
		sys.exit()
	# Argument 1 est l'adresse du serveur
	host = sys.argv[1]
	# Argument 2 le port du serveur
	port = int(sys.argv[2])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)

	# Test de connexion 
	try :
		s.connect((host, port))
	except :
		print('Unable to connect')
		sys.exit()

	print('Connected to remote host. Start sending messages :')
	prompt()

	# démarage de la boucle infinie
	while 1:
		socket_list = [sys.stdin, s]

		ready = select.select(socket_list , [], [])

		# Pour chaque message à lire 
		for sock in ready[0]:
			# Si le message vient du socket
			if sock == s:
				data = sock.recv(4096)
				# Si c'est vide c'est que l'on est déconnecté
				if not data :
					print('\nDisconnected from chat server')
					sys.exit()
				# Sinon on l'écrit sur la console
				else :
					sys.stdout.write(data.decode("utf-8") + "\n")
					prompt()

			# Si le message vient de l'entrée standard, on l'envoie 
			else :
				msg = sys.stdin.readline()
				# To try with multiple data sending in one packet
				if msg[0:1] == 'ß':
					# You're going to shit on :
					s.send(msg[1:len(msg) - 1].encode('utf-8'))
				else:
					s.send(PrepareSending(msg[:len(msg) - 1]))

				prompt()