import ui, os, paramiko

class SFTPclient(ui.View):

  def __init__(self):
    self.localFile = ''
    self.remoteFile = ''
    self.connect = False
    self.sftp = None
    self.transport = None
    self.root = os.path.expanduser('~')
    self.path = os.getcwd()
    pos = self.path.rfind('/')
    self.cpath = self.path[pos:]
    self.view = ui.load_view('SFTPclient')
    bt1 = self.view['button1']
    bt1.action = self.bt_connect
    bt2 = self.view['button2']
    bt2.action = self.bt_upload
    bt3 = self.view['button3']
    bt3.action = self.bt_download
    self.tv1 = self.view['tableview1']
    self.tv2 = self.view['tableview2']
    self.txtv = self.view['textview1']
    self.remotePath = '/home/' + self.view['textfield2'].text #user
    all = self.get_dir()
    self.lst1 = ui.ListDataSource(all)
    self.tv1.data_source = self.lst1
    self.tv1.delegate = self.lst1
    self.tv1.editing = False
    self.lst1.font = ('Courier',14)
    self.lst1.action = self.table1_tapped
    self.lst1.delete_enabled = False 
    self.lst2 = ui.ListDataSource([''])
    self.tv2.data_source = self.lst2
    self.tv2.delegate = self.lst2
    self.tv2.editing = False
    self.lst2.font = ('Courier',14)
    self.lst2.action = self.table2_tapped
    self.lst2.delete_enabled = False 
    self.view.present('fullscreen')

  def bt_connect(self, sender):
    host = self.view['textfield1'].text
    user = self.view['textfield2'].text
    password = self.view['textfield3'].text
    port = 22
    if self.connect:
      self.connect = False 
      self.sftp.close()
      self.transport.close()
      sender.title = 'Connect'
      self.txtv.text = ''
    else:
      self.connect = True
      self.transport = paramiko.Transport((host, port))
      self.transport.connect(username = user, password = password)
      self.sftp = paramiko.SFTPClient.from_transport(self.transport)
      remoteDir  = [] if self.remotePath == '/' else ['/..']
      files = []
      attr = self.sftp.listdir_attr(self.remotePath)
      for entry in attr:
        if str(entry)[0] == 'd':
          remoteDir.append('/' + str(entry)[55:])
        else:
          files.append(str(entry)[55:])
      all = sorted(remoteDir)
      for file in sorted(files):
        all.append('{}'.format(file))
      self.refresh_table(self.tv2,self.lst2,all)
      sender.title = 'Disconnect'
      self.txtv.text = 'Connect with ' + host + ':' + str(port) + '\n'
      #self.txtv.text += 'user: ' + user + ', password: ' + password + '\n'
      #self.txtv.text += 'remotePath: ' + self.remotePath + '\n'

  def bt_upload(self, sender):
    if self.connect:
      pos = self.localFile.rfind('/')
      fileName = self.localFile[pos+1:]
      self.txtv.text += 'put(' + self.localFile + ', ' + self.remotePath + '/' + fileName + ')' + '\n'
      self.sftp.put(self.localFile, self.remotePath + '/' + fileName)
      all = self.get_remote_dir()
      self.refresh_table(self.tv2,self.lst2,all)

  def bt_download(self, sender):
    if self.connect:
      pos = self.remoteFile.rfind('/')
      fileName = self.remoteFile[pos+1:]
      self.txtv.text += 'get(' + self.remoteFile + ', ' + fileName + ')' + '\n'
      self.sftp.get(self.remoteFile, fileName)
      all = self.get_dir()
      self.refresh_table(self.tv1,self.lst1,all)

  def table1_tapped(self, sender):
    rowtext = sender.items[sender.selected_row]
    filename_tapped = rowtext
    if rowtext[0] == '/':
      if filename_tapped == '/..':
        pos = self.path.rfind('/')
        self.path = self.path[:pos]
      else:
        self.path = self.path + filename_tapped
      all = self.get_dir()
      self.view.name = self.path
      self.refresh_table(self.view['tableview1'],self.lst1,all)
    else:
      self.localFile = self.path + '/' + filename_tapped

  def table2_tapped(self, sender):
    rowtext = sender.items[sender.selected_row]
    filename_tapped = rowtext
    if rowtext[0] == '/':
      if filename_tapped == '/..':
        pos = self.remotePath.rfind('/')
        self.remotePath = self.remotePath[:pos]
        if self.remotePath == '':
          self.remotePath = '/'
      else:
        if self.remotePath == '/':
          self.remotePath = filename_tapped
        else:
          self.remotePath = self.remotePath + filename_tapped
      all = self.get_remote_dir()
      self.refresh_table(self.tv2,self.lst2,all)
      self.txtv.text = 'remotePath: ' + self.remotePath + '\n' + self.txtv.text
    else:
      self.remoteFile = self.remotePath + '/' + filename_tapped

  def refresh_table(self, table, lst, data):
    lst = ui.ListDataSource(data)
    table.data_source = lst
    table.delegate = lst
    table.editing = False
    lst.font = ('Courier',14)
    if table.name == 'tableview1':
      lst.action = self.table1_tapped
    else:
      lst.action = self.table2_tapped
    lst.delete_enabled = False 
    table.reload_data()
    return

  def get_dir(self):
    dirs  = [] if self.path == self.root else ['..']
    files = []
    for entry in sorted(os.listdir(self.path)):
      if os.path.isdir(self.path + '/' + entry):
        dirs.append(entry)
      else:
        files.append(entry)
    all = ['/' + dir for dir in dirs]
    for file in files:
      full_pathname = self.path + '/' + file
      all.append('{}'.format(file))
    return all

  def get_remote_dir(self):
    remoteDir  = [] if self.remotePath == '/' else ['/..']
    files = []
    attr = self.sftp.listdir_attr(self.remotePath)
    for entry in attr:
      if str(entry)[0] ==  'd':
        remoteDir.append('/' + str(entry)[55:])
      else:
        files.append(str(entry)[55:])
    all = sorted(remoteDir)
    for file in sorted(files):
      all.append('{}'.format(file))
    return all

SFTPclient()
