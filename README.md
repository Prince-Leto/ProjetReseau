# LISS Plugin

### Features :
- Instant communication
- Multiple file on server
	- Create file
	- Connect to a file
- Others's Cursors
- Multiple tab support
- Ability to lock a line
- Save data in real file

### Todo :
- Fixe bugs
- Test Windows compatibility
- Add plugin to wbond

### How to :
Place project files into your sublime packages directory - commonly ~/.config/sublime-text-3/Packages/ - in a new folder called LISS.

Start server using `python3 Socket/Serveur.py 5000`

In order to debug you can start a console client `python3 Socket/Client.py localhost 5000`

And start using our plugin. You can do « Connect this file | ctrl+shift+i » on an empty file to start using your server.

### Data convention

All transfered data end with '\x01' in order to reconstruct messages

#####Client examples :
- Cursors :
	- `k1,1`
	- `k0,0|5,10`

- Requesting for the file list :
	- `GetFiles`

- Creating a new file :
	- `cNewFile`
	- `cTest`

- Inserting text : Size of the old text + '|' + insertion
	- `0|i0,Hello World ! + '\x00'`
	- `13|i0,Goodbye\n + '\x00'`

- Deleting text :
	- `22|d0,1 + '\x00'`
	- `21|d1,10 + '\x00'`

#####Server example :
- Send the file list :
	- `fNewFile,Test`

- Resend cursors :
	- `k44473:1,1`
	- `k44475:0,0|5,10`

- Reset the content :
	- `n,File content.`
