import threading, socket, select

import sublime, sublime_plugin

client = 0
views = []
cursors = []
old = []
data = 0
dataReceived = 0

HOST = 'localhost'
PORT = 5003
BUFFER = 4096

class TestCommand(sublime_plugin.TextCommand):
	def run(self, view):
		self.view.add_regions('ColorTest', [sublime.Region(3, 3)], "string", "dot", sublime.DRAW_EMPTY)

class CreateFileCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client
		if client != 0:
			window = sublime.active_window()
			def onDone(m):
				global client
				client.send(("c" + m).encode("utf-8"))

			window.show_input_panel("Name", "", onDone, None, None)

class RemoteFileCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client
		if client != 0:
			client.send("GetFiles".encode("utf-8"))

class ListenCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client
		if not client == 0:
			client.close()
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect((HOST, PORT))
		self.view.run_command('add_view')

class AddViewCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global client, views, cursors, data, dataReceived
		if client != 0:
			if self.view not in views:
				views.append(self.view)
				cursors.append([])
				old.append([])

		def Listen():
			global client, data, dataReceived
			while 1:
				read, write, errors = select.select([client], [], [])
				for sock in read:
					data = sock.recv(BUFFER)
					if data:
						data = data.decode("utf-8")
						if data[0:1] == "i":
							dataReceived = 1
							self.view.run_command('insertion')
						elif data[0:1] == "d":
							dataReceived = 1
							self.view.run_command('deletion')
						elif data[0:1] == "n":
							dataReceived = 2
							self.view.run_command('erase')
							self.view.run_command('insertion')
						elif data[]
						elif data[0:1] == "f":
							if data != "f":
								def onDone(i):
									global sock
									if i != -1:
										sock.send(("f" + str(i)).encode("utf-8"))
								window = sublime.active_window()
								window.show_quick_panel(data[1:].split(","), onDone)
							else:
								sublime.error_message("No file available on server.")

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
						if cursors[e][i].begin() < view.sel()[i].begin():
							client.send(("i" + str(cursors[e][i].begin()) + "," + view.substr(sublime.Region(cursors[e][i].begin() + i, view.sel()[i].begin()))).encode("utf-8"))
						else:
							client.send(("d" + str(view.sel()[i].begin()) + "," + str(cursors[e][i].begin())).encode("utf-8"))
				else:
					dataReceived -= 1

	def on_selection_modified(self, view):
		global views, cursors, old
		if client != 0:
			if view in views:
				cursors[views.index(view)] = list(view.sel())
				client.send(("k" + str(cursors[views.index(view)])).encode("utf-8"))