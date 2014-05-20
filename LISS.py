import socket, sys
from select import select

import sublime, sublime_plugin

Sockets = []
Infos = []
Cursors = []
OCursors = []
Started = False
DataReceived = 0

Host = 'localhost'
Port = 5000
BUFFER = 4096

# SeparateData sépare les informations de manière logique, soit taille(0000-9999)+données
def SeparateData(param):
	m = []
	while len(param) > 0:
		m.append(param[4:4 + int(param[0:4])])
		param = param[4 + int(param[0:4]):]
	return m

# PrepareSending formate le message avec le nombre de charactère devant.
def PrepareSending(message):
	l = len(message)
	m = str(l)
	if l < 10000:
		for i in range(1,4):
			if l < 10**i:
				m = '0' + m
	else:
		sublime.error_message('Inserting too much text. Please reload the file.')
	return (m + message).encode('utf-8')

# ********************** Create File ********************************

# CreateFileCommand commande pour la création d'un fichier plus l'envoie au serveur
class CreateFileCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global Sockets, Infos
		def onDone(m):
			global Sockets, Infos
			try:
				index = Infos.index(sublime.active_window().active_view()) # Bad... But we cannot get parameters and I don't want an other global variable
				if ',' in m:
					sublime.error_message('File name not permited.')
				else:
					Sockets[index].send(PrepareSending('c' + m))
			except ValueError:
				sublime.error_message('This file is not connected.')
		sublime.active_window().show_input_panel('Name', '', onDone, None, None)

# ********************** Remote Files ********************************

# RemoteFileCommand envoie une demande de la liste des fichiers au serveur
class RemoteFileCommand(sublime_plugin.TextCommand):
	global Sockets, Infos
	def run(self, edit):
		try:
			Sockets[Infos.index(self.view)].send(PrepareSending('GetFiles'))
		except ValueError:
			sublime.error_message('This file is not connected.')

# ********************* Modify buffer ********************************

# Insertion de texte
class InsertionCommand(sublime_plugin.TextCommand):
	def run(self, edit, Data):
		status = self.view.is_read_only()
		self.view.set_read_only(False)
		self.view.insert(edit, int(Data.split(',', 1)[0]), Data.split(',', 1)[1])
		self.view.set_read_only(status)

# Suppression de texte
class DeletionCommand(sublime_plugin.TextCommand):
	def run(self, edit, Data):
		status = self.view.is_read_only()
		self.view.set_read_only(False)
		self.view.erase(edit, sublime.Region(int(Data.split(',', 1)[0]), int(Data.split(',', 1)[1])))
		self.view.set_read_only(status)

# Supprime l'ensemble du fichier
class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		status = self.view.is_read_only()
		self.view.set_read_only(False)
		self.view.erase(edit, sublime.Region(0, self.view.size()))
		self.view.set_read_only(status)

# Loop boucle infinie chargée d'écouter les sockets
def Loop():
	global Sockets, Infos, DataReceived, OCursors
	while True:
		# Ready = select(Sockets, [], [])
		# for sock in Ready[0]:
		for sock in Sockets:
			Data = sock.recv(BUFFER)
			if not Data:
				sublime.error_message('Connection lost.')
				sock.close()
				index = Sockets.index(sock)
				Sockets.remove(sock)
				del Infos[index]
				del Cursors[index]
			else:
				index = Sockets.index(sock)
				Data = Data.decode('utf-8')
				for Data in SeparateData(Data):
					if Data[0:1] == 'i':
						DataReceived = 1
						Infos[index].run_command('insertion', {'Data': Data[1:]})
					elif Data[0:1] == 'd':
						DataReceived = 1
						Infos[index].run_command('deletion', {'Data': Data[1:]})
					elif Data[0:1] == 'n':
						DataReceived = 0
						if Infos[index].size() > 0:
							DataReceived += 1
							Infos[index].run_command('erase')
						if Data[1:].split(',', 1)[1] != '':
							DataReceived += 1
							Infos[index].run_command('insertion', {'Data': Data[1:]})
					elif Data[0:1] == 'k':
						Addr = Data[1:].split(':')[0]
						Key = Data[1:].split(':')[1].split('|')
						for i in range(len(Key)):
							Key[i] = sublime.Region(int(Key[i].split(',')[0]), int(Key[i].split(',')[1]))
						OCursors[index] = Key
						Infos[index].add_regions(Addr, Key, 'string', 'dot', sublime.DRAW_EMPTY)
						Over = False
						for K in OCursors[index]:
							for L in Cursors[index]:			
								for l_other in Infos[index].lines(K):
									for l_me in Infos[index].lines(L):
										if l_me == l_other:
											Over = True

						Infos[index].set_read_only(Over)
					elif Data[0:1] == 'f':
						if Data != 'f':
							def onDone(i):
								global client
								if i != -1:
									Sockets[index].send(PrepareSending('f' + str(i)))
							sublime.active_window().show_quick_panel(Data[1:].split(','), onDone)
						else:
							sublime.error_message('No file available on server.')


class CreateSocketCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global Sockets, Infos, Cursors, OCursors, Started

		def onDone(message):
			global Sockets, Infos, Cursors, Started
			try:
				Host, Port = message.split(':', 1)
				Port = int(Port)

				Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				Infos.append(self.view)
				Cursors.append(list(self.view.sel()))
				OCursors.append([])

				try:
					Sock.connect((Host, Port))
					Sockets.append(Sock)
					if not Started:
						Started = True
						sublime.set_timeout_async(Loop, 0)

				except:
					sublime.error_message('Unable to connect.')
			except:
				sublime.error_message('Please enter hostname:port.')

		sublime.active_window().show_input_panel('Hostname:port', '', onDone, None, None)

# ************************ Retrieving Data **********************************


def FormatData(Cursors, View, i):
	if Cursors[i].begin() != Cursors[i].end():
		m = 'd' + str(Cursors[i].begin()) + ',' + str(Cursors[i].end())
		if Cursors[i].begin() < View.sel()[i].begin():
			m += '|i' + str(Cursors[i].begin()) + ',' + View.substr(sublime.Region(Cursors[i].begin() + i, View.sel()[i].begin()))
		return m
	else:
		if Cursors[i].begin() < View.sel()[i].begin():
			return 'i' + str(Cursors[i].begin()) + ',' + View.substr(sublime.Region(Cursors[i].begin() + i, View.sel()[i].begin()))
		elif Cursors[i].begin() > View.sel()[i].begin():
			return 'd' + str(View.sel()[i].begin()) + ',' + str(Cursors[i].begin())
		else:
			return ''

class ListenerCommand(sublime_plugin.EventListener):
	def on_modified(self, view):
		global Sockets, Infos, Cursors, DataReceived
		if DataReceived == 0:
			try:
				index = Infos.index(view)
				if len(view.sel()) != len(Cursors[index]):
					sublime.error_message('This situation sucks.')
				else:
					m = ''
					for i in range(len(view.sel()) - 1):
						m += FormatData(Cursors[index], view, i) + '|'
					m += FormatData(Cursors[index], view, len(view.sel()) - 1)
					Sockets[index].send(PrepareSending(m))

			except ValueError:
				pass
		else:
			DataReceived -= 1
	def on_selection_modified(self, view):
		global Sockets, Infos, Cursors, OCursors
		try:
			index = Infos.index(view)
			Cursors[index] = list(view.sel())
			m = ''
			for i in range(len(view.sel()) - 1):
				m += str(view.sel()[i].begin()) + ',' + str(view.sel()[i].end()) + '|'
			m += str(view.sel()[len(view.sel()) - 1].begin()) + ',' + str(view.sel()[len(view.sel()) - 1].end())
			Sockets[index].send(PrepareSending('k' + m))
			Over = False


			for K in OCursors[index]:
				for L in Cursors[index]:			
					for l_other in view.lines(K):
						for l_me in view.lines(L):
							if l_me == l_other:
					 			Over = True
			if Over and len(Cursors[index]) == 1 and Cursors[index][0].end() == Cursors[index][0].begin() and Cursors[index][0].begin() == view.size():
				DataReceived = 1
				view.run_command('insertion', {'Data': str(view.size()) + ',' + '\n'})

			view.set_read_only(Over)
	
		except ValueError:
			pass