import threading, socket, select

import sublime, sublime_plugin

client = 0
views = []
cursors = []
data = 0
dataReceived = 0

HOST = 'localhost'
PORT = 5003
BUFFER = 4096

def PrepareSending(message):
	l = len(message)
	m = str(l)
	if l < 10000:
		for i in range(1,4):
			if l < 10**i:
				m = "0" + m
	return (m + message).encode("utf-8")

class CreateFileCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client
		if client != 0:
			window = sublime.active_window()
			def onDone(m):
				global client
				client.send(PrepareSending("c" + m))

			window.show_input_panel("Name", "", onDone, None, None)

class RemoteFileCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client
		if client != 0:
			client.send(PrepareSending("GetFiles"))

class ListenCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client
		if client != 0:
			client.close()
		try:
			client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client.connect((HOST, PORT))
		except:
			sublime.error_message("Unable to connect.")
		self.view.run_command('add_view')

class AddViewCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client, views, cursors, data, dataReceived
		if client != 0:
			if self.view not in views:
				views.append(self.view)
				cursors.append([])

		def Listen():
			global client, data, dataReceived
			while 1:
				try:
					data = client.recv(BUFFER)
					data = data.decode("utf-8")
					print(data)
					if data[0:1] == "i":
						dataReceived = 1
						self.view.run_command('insertion')
					elif data[0:1] == "d":
						dataReceived = 1
						self.view.run_command('deletion')
					elif data[0:1] == "n":
						dataReceived = 0
						if self.view.size() > 0:
							dataReceived += 1
							self.view.run_command('erase')
						if data[1:].split(",", 1)[1] != '':
							dataReceived += 1
							self.view.run_command('insertion')
					elif data[0:1] == "k":
						addr = data[1:].split(":")[0]
						l = data[1:].split(":")[1].split("|")
						for i in range(len(l)):
							l[i] = sublime.Region(int(l[i].split(",")[0]),int(l[i].split(",")[1]))
						self.view.add_regions(addr, l, "string", "dot", sublime.DRAW_EMPTY)
					elif data[0:1] == "f":
						if data != "f":
							def onDone(i):
								global client
								if i != -1:
									client.send(PrepareSending("f" + str(i)))
							window = sublime.active_window()
							window.show_quick_panel(data[1:].split(","), onDone)
						else:
							sublime.error_message("No file available on server.")
				except:
					sublime.error_message("Connection lost.")

		sublime.set_timeout_async(Listen, 0)

class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global data
		self.view.erase(edit, sublime.Region(0, self.view.size()))

class InsertionCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global data
		self.view.insert(edit, int(data[1:].split(",", 1)[0]), data[1:].split(",", 1)[1])

class DeletionCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global data
		self.view.erase(edit, sublime.Region(int(data[1:].split(",", 1)[0]), int(data[1:].split(",", 1)[1])))

class ListenerCommand(sublime_plugin.EventListener):
	def on_modified(self, view):
		global client, views, cursors, dataReceived
		if client != 0:
			if view in views:
				if dataReceived == 0:
					e = views.index(view)
					for i in range(len(view.sel())):
						if cursors[e][i].begin() != cursors[e][i].end():
							client.send(PrepareSending("d" + str(cursors[e][i].begin()) + "," + str(cursors[e][i].end())))
							if cursors[e][i].begin() < view.sel()[i].begin():
								client.send(PrepareSending("i" + str(cursors[e][i].begin()) + "," + view.substr(sublime.Region(cursors[e][i].begin() + i, view.sel()[i].begin()))))
						else:
							if cursors[e][i].begin() < view.sel()[i].begin():
								client.send(PrepareSending("i" + str(cursors[e][i].begin()) + "," + view.substr(sublime.Region(cursors[e][i].begin() + i, view.sel()[i].begin()))))
							else:
								client.send(PrepareSending("d" + str(view.sel()[i].begin()) + "," + str(cursors[e][i].begin())))
				else:
					dataReceived -= 1

	def on_selection_modified(self, view):
		global views, cursors
		if client != 0:
			if view in views:
				cursors[views.index(view)] = list(view.sel())
				m = ''
				for i in range(len(view.sel()) - 1):
					m += str(view.sel()[i].begin()) + "," + str(view.sel()[i].end()) + "|"
				m += str(view.sel()[len(view.sel()) - 1].begin()) + "," + str(view.sel()[len(view.sel()) - 1].end())
				client.send(PrepareSending("k" + m))