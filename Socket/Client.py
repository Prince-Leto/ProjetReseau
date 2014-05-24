import socket, select, sys

def prompt() :
	sys.stdout.write('-> ')
	sys.stdout.flush()

if __name__ == "__main__":

	if(len(sys.argv) < 3) :
		print('Usage : python3 Client.py hostname port')
		sys.exit()
	host = sys.argv[1]
	port = int(sys.argv[2])

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)

	try :
		s.connect((host, port))
	except :
		print('Unable to connect')
		sys.exit()

	print('Connected to remote host. Start sending messages :')
	prompt()

	while True:
		socket_list = [sys.stdin, s]
		ready = select.select(socket_list , [], [])

		for sock in ready[0]:
			if sock == s:
				data = sock.recv(4096)
				if not data :
					print('\nDisconnected from chat server')
					sys.exit()
				else :
					sys.stdout.write(data.decode("utf-8") + "\n")
					prompt()

			else :
				msg = sys.stdin.readline()
				if msg[0] == 'ß':
					s.send(('Coucou' + chr(0) + 'Bref').encode('utf-8'))
				else:
					s.send(msg[0:len(msg) - 1].encode('utf-8'))

				prompt()