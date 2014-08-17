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
    self.view = ui.load_view('SFTPclient03')
    self.view['bt_connect'].action = self.bt_connect
    self.view['bt_upload'].action = self.bt_upload
    self.view['bt_download'].action = self.bt_download
    root_len = len(self.root)
    self.view['lb_local'].text = self.path[root_len:]
    self.tv_local = self.view['tv_local']
    self.tv_remote = self.view['tv_remote']
    self.tv_info = self.view['tv_info']
    self.remotePath = '/home/' + self.view['tf_user'].text
    all = self.get_dir()
    self.lst_local = ui.ListDataSource(all)
    self.tv_local.data_source = self.lst_local
    self.tv_local.delegate = self.lst_local
    self.tv_local.editing = False
    self.lst_local.font = ('Courier',14)
    self.lst_local.action = self.table_local_tapped
    self.lst_local.delete_enabled = False 
    self.lst_remote = ui.ListDataSource([''])
    self.tv_remote.data_source = self.lst_remote
    self.tv_remote.delegate = self.lst_remote
    self.tv_remote.editing = False
    self.lst_remote.font = ('Courier',14)
    self.lst_remote.action = self.table_remote_tapped
    self.lst_remote.delete_enabled = False 
    self.view.present('fullscreen')

  def bt_connect(self, sender):
    host = self.view['tf_host'].text
    user = self.view['tf_user'].text
    password = self.view['tf_password'].text
    port = 22
    if self.connect:
      self.connect = False 
      self.sftp.close()
      self.transport.close()
      sender.title = 'Connect'
      self.tv_info.text = ''
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
      self.refresh_table(self.tv_remote,self.lst_remote,all)
      self.view['lb_remote'].text = self.remotePath
      sender.title = 'Disconnect'
      self.tv_info.text = 'Connect with ' + host + ':' + str(port) + '\n'
      #self.tv_info.text = 'user: ' + user + ', password: ' + password + '\n' + self.tv_info.text
      #self.tv_info.text = 'remotePath: ' + self.remotePath + '\n' + self.tv_info.text

  def bt_upload(self, sender):
    if self.connect:
      pos = self.localFile.rfind('/')
      fileName = self.localFile[pos+1:]
      self.tv_info.text = 'put(' + self.localFile + ', ' + self.remotePath + '/' + fileName + ')' + '\n' + self.tv_info.text
      self.sftp.put(self.localFile, self.remotePath + '/' + fileName)
      all = self.get_remote_dir()
      self.refresh_table(self.tv_remote,self.lst_remote,all)

  def bt_download(self, sender):
    if self.connect:
      pos = self.remoteFile.rfind('/')
      fileName = self.remoteFile[pos+1:]
      self.tv_info.text = 'get(' + self.remoteFile + ', ' + fileName + ')' + '\n' + self.tv_info.text
      self.sftp.get(self.remoteFile, fileName)
      all = self.get_dir()
      self.refresh_table(self.tv_local,self.lst_local,all)

  def table_local_tapped(self, sender):
    rowtext = sender.items[sender.selected_row]
    filename_tapped = rowtext
    if rowtext[0] == '/':
      if filename_tapped == '/..':
        pos = self.path.rfind('/')
        self.path = self.path[:pos]
      else:
        self.path = self.path + filename_tapped
      all = self.get_dir()
      #self.view.name = self.path
      root_len = len(self.root)
      self.view['lb_local'].text = self.path[root_len:]
      self.refresh_table(self.view['tv_local'],self.lst_local,all)
    else:
      self.localFile = self.path + '/' + filename_tapped

  def table_remote_tapped(self, sender):
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
      self.refresh_table(self.tv_remote,self.lst_remote,all)
      #self.tv_info.text = 'remotePath: ' + self.remotePath + '\n' + self.tv_info.text
      self.view['lb_remote'].text = self.remotePath
    else:
      self.remoteFile = self.remotePath + '/' + filename_tapped

  def refresh_table(self, table, lst, data):
    lst = ui.ListDataSource(data)
    table.data_source = lst
    table.delegate = lst
    table.editing = False
    lst.font = ('Courier',14)
    if table.name == 'tv_local':
      lst.action = self.table_local_tapped
    else:
      lst.action = self.table_remote_tapped
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
