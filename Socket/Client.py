import socket, select, sys

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

	while 1:
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
				# To try with multiple data sending in one packet
				if msg[0:1] == 'ß':
					# You're going to shit on :
					s.send(msg[1:len(msg) - 1].encode('utf-8'))
				else:
					s.send(PrepareSending(msg[:len(msg) - 1]))

				prompt()