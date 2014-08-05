import ui, os, paramiko, urllib

def refresh_table(table, lst, data):
    global tv1, tv2
    lst = ui.ListDataSource(data)
    table.data_source = lst
    table.delegate = lst
    table.editing = False
    lst.font = ('Courier',14)
    if table == tv1:
        lst.action = table1_tapped
    else:
        lst.action = table2_tapped
    lst.delete_enabled = False 
    table.reload_data()
    return

def get_dir(path):
    dirs  = [] if path == root else ['..']
    files = []
    for entry in sorted(os.listdir(path)):
        if os.path.isdir(path + '/' + entry):
            dirs.append(entry)
        else:
            files.append(entry)
    all = ['/' + dir for dir in dirs]
    for file in files:
        full_pathname = path + '/' + file
        all.append('{}'.format(file))
    return all

def get_remote_dir(remotePath):
    global sftp, txtv
    remoteDir  = [] if remotePath == '/' else ['/..']
    files = []
    txtv.text += 'remotePath: ' + remotePath + '\n'
    attr = sftp.listdir_attr(remotePath)
    for entry in attr:
        if str(entry)[0] ==  'd':
            remoteDir.append('/' + str(entry)[55:])
        else:
            files.append(str(entry)[55:])
    all = sorted(remoteDir)
    for file in sorted(files):
        all.append('{}'.format(file))
    return all

def bt_connect(sender):
    global host, user, password, connect, sftp, transport, tv2, lst2, remotePath, txtv
    port = 22
    if connect:
        connect = False 
        sftp.close()
        transport.close()
        sender.title = 'Connect'
        txtv.text = ''
    else:
        connect = True
        transport = paramiko.Transport((host, port))
        transport.connect(username = user, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        remoteDir  = [] if remotePath == '/' else ['/..']
        files = []
        attr = sftp.listdir_attr(remotePath)
        for entry in attr:
            if str(entry)[0] == 'd':
                remoteDir.append('/' + str(entry)[55:])
            else:
                files.append(str(entry)[55:])
        all = sorted(remoteDir)
        for file in sorted(files):
            all.append('{}'.format(file))
        refresh_table(tv2,lst2,all)
        sender.title = 'Disconnect'
        txtv.text += 'connect with ' + host + ':' + str(port) + '\n'
        #txtv.text += 'user: ' + user + ', password: ' + password + '\n'
        #txtv.text += 'remotePath: ' + remotePath + '\n'
    return

def bt_upload(sender):
    global connect, sftp, transport, localFile, remotePath, txtv, tv2, lst2
    if connect:
        pos = localFile.rfind('/')
        fileName = localFile[pos+1:]
        txtv.text += 'put(' + localFile + ', ' + remotePath + '/' + fileName + ')' + '\n'
        sftp.put(localFile, remotePath + '/' + fileName)
        all = get_remote_dir(remotePath)
        refresh_table(tv2,lst2,all)
    return

def bt_download(sender):
    global connect, sftp, transport, remoteFile, path, txtv, tv1, lst1
    if connect:
        pos = remoteFile.rfind('/')
        fileName = remoteFile[pos+1:]
        txtv.text += 'get(' + remoteFile + ', ' + fileName + ')' + '\n'
        sftp.get(remoteFile, fileName)
        all = get_dir(path)
        refresh_table(tv1,lst1,all)
    return

def table1_tapped(sender):
    global path, buffer, tv1, lst1, localFile, txtv
    rowtext = sender.items[sender.selected_row]
    filename_tapped = rowtext
    if rowtext[0] == '/':
        if filename_tapped == '/..':
            pos = path.rfind('/')
            path = path[:pos]
        else:
            path = path + filename_tapped
        all = get_dir(path)
        view.name = path
        refresh_table(tv1,lst1,all)
    else:
        localFile = path + '/' + filename_tapped
    txtv.text += 'localPath: ' + path + '\n'
    return

def table2_tapped(sender):
    global sftp, remotePath, tv2, lst2, remoteFile, txtv
    rowtext = sender.items[sender.selected_row]
    filename_tapped = rowtext
    if rowtext[0] == '/':
        if filename_tapped == '/..':
            pos = remotePath.rfind('/')
            remotePath = remotePath[:pos]
            if remotePath == '':
                remotePath = '/'
        else:
            if remotePath == '/':
                remotePath = filename_tapped
            else:
                remotePath = remotePath + filename_tapped
        all = get_remote_dir(remotePath)
        refresh_table(tv2,lst2,all)
    else:
        remoteFile = remotePath + '/' + filename_tapped
    txtv.text += 'remotePath: ' + remotePath + '\n'
    return

localFile = ''
remoteFile = ''
connect = False
sftp = None
transport = None
root = os.path.expanduser('~')
path = os.getcwd()
all = get_dir(path)
pos = path.rfind('/')
cpath = path[pos:]
	
view = ui.load_view('SFTPclient')
tf1 = view['textfield1']
host = tf1.text
tf2 = view['textfield2']
user = tf2.text
tf3 = view['textfield3']
password = tf3.text
remotePath = '/home/' + user
bt1 = view['button1']
bt1.action = bt_connect
bt2 = view['button2']
bt2.action = bt_upload
bt3 = view['button3']
bt3.action = bt_download
tv1 = view['tableview1']
tv2 = view['tableview2']
txtv = view['textview1']

lst1 = ui.ListDataSource(all)
tv1.data_source = lst1
tv1.delegate = lst1
tv1.editing = False
lst1.font = ('Courier',14)
lst1.action = table1_tapped
lst1.delete_enabled = False 

lst2 = ui.ListDataSource([''])
tv2.data_source = lst2
tv2.delegate = lst2
tv2.editing = False
lst2.font = ('Courier',14)
lst2.action = table2_tapped
lst2.delete_enabled = False 

view.present('fullscreen')
