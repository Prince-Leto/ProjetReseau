# LISS Plugin

### Features :
- Instant communication
- Multiple file on server
	- Create file
	- Connect to a file
- Others's Cursors
- Multiple tab support

### Todo :
- Windows Compatibility
- Fixe bugs
- Ability to lock a line

### How to :
Place project files into your sublime packages directory - commonly ~/.config/sublime-text-3/Packages/ - in a new folder called LISS.

Start server using `python3 Socket/Serveur.py 5000`

In order to debug you can start a console client `python3 Socket/Client.py localhost 5000`

And start using our plugin. You can do « Connect this file | ctrl+shift+i » on an empty file to start using your server.