#!/usr/bin/env python
import logging
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from sys import argv, exit
from time import time
from time import time
import datetime
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import sys, pickle, xmlrpclib
from xmlrpclib import Binary
import socket
import errno
from socket import error
from errno import ECONNREFUSED

count = 0

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

if not hasattr(__builtins__, 'bytes'):
    bytes = str



class FileNode:
    def __init__(self,name,isFile,path,ports):
	print "In FileNode"
	now = time()
        self.name = name
        self.path = path
        self.ports = ports
        self.isFile = isFile # true if node is a file, false if is a directory.
        self.put("data","") # used if it is a file
        self.put("meta",{})
        self.put("list_nodes",{})# contains a tuple of <name:FileNode>  used only if it is a dir. 
	self.server_down_list = []
	self.files = {}

    def put(self,key,value):
        key_1 = self.path+"&&"+key
	print key 
	if key == 'data':
		ports_d = ports[5:]
		status_of_servers = self.check_server_status()
		print status_of_servers
		if status_of_servers == False:
			print "Write Server is down so write will not complete"
			return None
		else:
			print status_of_servers
			print ports[3]
			print "Before second loop"			
			for port in ports_d:
				print port
				url = str("http://127.0.0.1:"+str(port))
				print str(url) + "Here in second for loop"
				rpc = xmlrpclib.Server(url)
				rpc.put(Binary(key_1), Binary(pickle.dumps(value)), 3000)
	else:
		rpc = xmlrpclib.Server(str("http://127.0.0.1:"+str(ports[4])))
		try:
			rpc.put(Binary(key_1), Binary(pickle.dumps(value)), 3000)
		except:
			return None
				
		
		
		
			
    def get(self,key):
        key_1 = self.path+"&&"+key
	print key_1 + "Here Key_1"
	list_index = []
	list_index1 = []
	output = 0
	res = ''
	qr = 0
	x = 0 # Number of servers that are up and running
	print "In Get"
	if key == 'data':
		self.files_list = []
		self.files_list1 = []
		ports_d = ports[5:]
		for port in ports_d:
			url = "http://127.0.0.1:"+str(port)		
			rpc = xmlrpclib.Server(url)
			try:
				res = rpc.get(Binary(key_1))
				if "value" in res:
					output = pickle.loads(res["value"].data)
					output1 = pickle.loads(res["value"].data)
					self.files_list.append(pickle.loads(res["value"].data))
					self.files_list1.append(pickle.loads(res["value"].data))
					print "key"
					print pickle.loads(res["value"].data)
					print key_1
					print "dict"
				else:
					self.files_list1.append('')
					print "In else of get-if"
					continue	
		 	except socket.error as serr:
				print "Read server is down", serr
				continue
			
				print self.files_list
			
		#return pickle.loads(res["value"].data)
		if self.files_list:
			qr_set = self.read_quorum_check(self.files_list)
			print "qr_set" + str(qr_set)
			if qr_set:
				list_index = self.check_for_index(self.files_list)	#list of servers to be updated
				list_index1 = self.check_for_index1(self.files_list)	#list of servers with correct values
				self.update_server(list_index, list_index1,key_1, ports_d)
				return output
			else:
				print "I am in get else part"
				return "Not enough to read"
		else:
			print "I am in second if part"
			return "Not enough to read"
	else:
		rpc = xmlrpclib.Server(str("http://127.0.0.1:"+str(ports[4])))
		res = rpc.get(Binary(key_1))
		if "value" in res:
			return pickle.loads(res["value"].data)



    def update_server(self,list_index, list_index1, key_1,ports_d):
	list0 = list_index			#list of servers to be updated
	list1 = list_index1			#list of servers with correct values
	for n1 in list0:
		print "In update server"
		port = ports_d[list1[0]]
		print port
		url = "http://127.0.0.1:"+str(port)		
		rpc = xmlrpclib.Server(url)
		res = rpc.get(Binary(key_1))
		output = pickle.loads(res["value"].data)
		print "n1"+str(n1)
		print output
		port2 = ports_d[n1]
		print port2
		url2 = "http://127.0.0.1:"+str(port2)
		rpc2 = xmlrpclib.Server(url2)
		try:
			rpc2.put(Binary(key_1), Binary(pickle.dumps(output)), 3000)
		except socket.error as serr:
			print "Server down while updating", serr


    def check_server_status(self):
	no_of_server = 0
	#check for the read servers if they fulfill the read conditions or not
	ports_d = ports[5:]
	for port in ports_d:
			url = str("http://127.0.0.1:"+str(port))
			print port
			print str(url) + "Here"
			rpc = xmlrpclib.Server(url)
			try:           
				print "In 1" + str(url)  
				rpc.ping()
			except socket.error as serr:
				print "Write Server is down",str(url), serr
				return False
	print "Again"
	return True
	
    def read_quorum_check(self, files_list):
	files = self.files_list
	if int(self.ports[2])>3:
		qr=0
	else:
		qr=1
	n=1
	print len(files_list)
	for key1 in files_list[:]:
		for key2 in files_list[n:]:
			if key1 == key2:
				qr+=1
				print self.ports[2]
				if qr >= int(self.ports[2]):
					return True
				print key1,key2,"Read Quorum satisfied:"
		n+=1
	print qr
	return False	

    def check_for_index(self,files_list1):
	files = self.files_list1
	list_index = []
	n=1
	print files
	for i1 in range(0,len(files)):
                print 'i1',i1 
                print len(files)    
		qr=1          
		for i2 in range(0,len(files)):
                        print 'i2',i2
	                if i1!= i2 and files[i1]==files[i2]:
				qr+=1
				print "Index Quorum checking:"+str(qr)
		print qr
                print 'i1:1', i1
		if qr < int(self.ports[2]):
                        print 'i1:2',i1
			list_index.append(i1)
	print "0" + str(list_index)
	return list_index

    def check_for_index1(self,files_list1):
	files = self.files_list1
	list_index1 = []
	n=1
	print files
	for i1 in range(0,len(files)):
                print 'i1',i1 
                print len(files)    
		qr=1          
		for i2 in range(0,len(files)):
                        print 'i2',i2
			if i1!= i2 and files[i1]==files[i2]:
				qr+=1
				print "Index Quorum checking:"
		if qr >= int(self.ports[2]):
			list_index1.append(i1)
	print qr
	print "1" + str(list_index1)
	return list_index1
		

	
    def set_data(self,data_blob):
        self.put("data",data)
        

    def set_meta(self,meta):
        self.put("meta",meta)

    def get_data(self):
        return self.get("data")

    def get_meta(self):
        return self.get("meta")

    def list_nodes(self):
        return self.get("list_nodes").values()

    def add_node(self,newnode):
        list_nodes = self.get("list_nodes")
        list_nodes[newnode.name]=newnode
        self.put("list_nodes",list_nodes)

    def contains_node(self,name): # returns node object if it exists
        if (self.isFile==True):
            return None
        else:
            if name in self.get("list_nodes").keys():
                return self.get("list_nodes")[name]
            else:
                return None


class FS:
    def __init__(self,ports):
        self.ports = ports
        self.root = FileNode('/',False,'/',ports)
        now = time()
        self.fd = 0
	print "Here in FS"
        out = self.root.set_meta(dict(st_mode=(S_IFDIR | 0755), st_ctime=now,st_mtime=now,\
                                         st_atime=now, st_nlink=2))
	if out == False:
		print "Server is down"

    # returns the desired FileNode object
    def get_node_wrapper(self,path): # pathname of the file being probed.
        # Handle special case for root node
        if path == '/':
            return self.root
        PATH = path.split('/') # break pathname into a list of components
        name = PATH[-1]
        PATH[0]='/' # splitting of a '/' leading string yields "" in first slot.
        return self.get_node(self.root,PATH,name) 


    def get_node(self,parent,PATH,name):
        next_node = parent.contains_node(PATH[1])
        if (next_node == None or next_node.name == name):
            return next_node
        else:
            return self.get_node(next_node,PATH[1:],name)

    def get_parent_node(self,path):
        parent_path = "/"+("/".join(path.split('/')[1:-1]))
        parent_node = self.get_node_wrapper(parent_path)
        return parent_node

    def add_node(self,node,path):
        parent_path = "/"+("/".join(path.split('/')[1:-1]))
        parent_node = self.get_node_wrapper(parent_path)
        parent_node.add_node(node)
        if (not node.isFile):
            meta = parent_node.get("meta")
            meta['st_nlink']+=1
            parent_node.put("meta",meta)
        else:
            self.fd+=1
            return self.fd

    def add_dir(self,path,mode):
        # create a file node
        temp_node = FileNode(path.split('/')[-1],False,path,self.ports)
        temp_node.set_meta(dict(st_mode=(S_IFDIR | mode), st_nlink=2,
                                st_size=0, st_ctime=time(), st_mtime=time(),
                                st_atime=time()))
        # Add node to the FS
        self.add_node(temp_node,path)
  

    def add_file(self,path,mode):
        # create a file node
        temp_node = FileNode(path.split('/')[-1],True,path,self.ports)
        temp_node.set_meta(dict(st_mode=(S_IFREG | mode), st_nlink=1,
        st_size=0, st_ctime=time(), st_mtime=time(),
        st_atime=time()))
        # Add node to the FS
        # before we do that, we have to manipulate the path string to point
        self.add_node(temp_node,path)
        self.fd+=1
        return self.fd

    def write_file(self,path,data=None, offset=0, fh=None):
        # file will already have been created before this call
        # get the corresponding file node
        filenode = self.get_node_wrapper(path)
	print "data from attrib"
	print data
        # if data == None, this is just a truncate request,using offset as 
        # truncation parameter equivalent to length
        node_data = filenode.get("data")
	#print node_data
        node_meta = filenode.get("meta")
	print "node_data" + str(node_data)
        if (data==None):
            node_data = node_data[:offset]
	    
            node_meta['st_size'] = offset
        else:
            node_data = node_data[:offset]+data
            node_meta['st_size'] = len(node_data)
        filenode.put("data",node_data)
        filenode.put("meta",node_meta)
        

    def read_file(self,path,offset=0,size=None):
        # get file node
        filenode = self.get_node_wrapper(path)
        # if size==None, this is a readLink request
        if (size==None):
            return filenode.get_data()
        else:
            # return requested portion data
            return filenode.get("data")[offset:offset + size]

    def rename_node(self,old,new):
        # first check if parent exists i.e. destination path is valid
        future_parent_node = self.get_parent_node(new)
        if (future_parent_node == None):
            raise  FuseOSError(ENOENT)
            return
        # get old filenodeobject and its parent filenode object
        filenode = self.get_node_wrapper(old)
        parent_filenode = self.get_parent_node(old)
        # remove node from parent
        list_nodes = parent_filenode.get("list_nodes")
        del list_nodes[filenode.name]
        parent_filenode.put("list_nodes",list_nodes)
        # if filenode is a directory decrement 'st_link' of parent
        if (not filenode.isFile):
            parent_meta = parent_filenode.get("meta")
            parent_meta["st_nlink"]-=1
            parent_filenode.put("meta",parent_meta)
        # add filenode to new parent, also change the name
        filenode.name = new.split('/')[-1]
        future_parent_node.add_node(filenode)

    def utimens(self,path,times):
        filenode = self.get_node_wrapper(path)
        now = time()
        atime, mtime = times if times else (now, now)
        meta = filenode.get("meta")
        meta['st_atime'] = atime
        meta['st_mtime'] = mtime
        filenode.put("meta",meta)

    def delete_node(self,path):
        # get parent node
        parent_filenode = self.get_parent_node(path)
        # get node to be deleted
        filenode = self.get_node_wrapper(path)
        # remove node from parents list
        list_nodes = parent_filenode.get("list_nodes")
        del list_nodes[filenode.name]
        parent_filenode.put("list_nodes",list_nodes)
        # if its a dir reduce 'st_nlink' in parent
        if (not filenode.isFile):
            parents_meta = parent_filenode.get("meta")
            parents_meta["st_nlink"]-=1
            parent_filenode.put("meta",parents_meta)

    def link_nodes(self,target,source):
        # create a new target node.
        temp_node = FileNode(target.split('/')[-1],True,path,self.ht)
        temp_node.set_meta(dict(st_mode=(S_IFLNK | 0777), st_nlink=1,
                                  st_size=len(source)))
        temp_node.set_data(source)
        # add the new node to FS
        self.add_node(temp_node,target)

    def update_meta(self,path,mode=None,uid=None,gid=None):
        # get the desired filenode.
        filenode = self.get_node_wrapper(path)
        # if chmod request
        meta = filenode.get("meta")
        if (uid==None):
            meta["st_mode"] &= 0770000
            meta["st_mode"] |= mode
        else: # a chown request
            meta['st_uid'] = uid
            meta['st_gid'] = gid
        filenode.put("meta",meta)

class Memory(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self,ports):
        global count # count is a global variable, can be used inside any function.
        count +=1 # increment count for very method call, to track count of calls made.
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time())) # print the parameters passed to the method as input.(used for debugging)
        print('In function __init__()') #print name of the method called

        self.FS = FS(ports)
       
        
       
        
    def getattr(self, path, fh=None):
        global count
        count +=1
        print ("CallCount {} " " Time {} arguments:{} {} {}".format(count,datetime.datetime.now().time(),type(self),path,type(fh)))
        print('In function getattr()')
        
        file_node =  self.FS.get_node_wrapper(path)
        if (file_node == None):
            raise FuseOSError(ENOENT)
        else:
            return file_node.get_meta()


    def readdir(self, path, fh):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function readdir()')

        file_node =  self.FS.get_node_wrapper(path)
        m = ['.','..']+[x.name for x in file_node.list_nodes()]
        print m
        return m

    def mkdir(self, path, mode):
        global count
        count +=1
        print ("CallCount {} " " Time {}" "," "argumnets:" " " "path;{}" "," "mode:{}".format(count,datetime.datetime.now().time(),path,mode))
        print('In function mkdir()')       
        # create a file node
        self.FS.add_dir(path,mode)

    def create(self, path, mode):
        global count
        count +=1
        print ("CallCount {} " " Time {} path {} mode {}".format(count,datetime.datetime.now().time(),path,mode))
        print('In function create()')
        
        return self.FS.add_file(path,mode) # returns incremented fd.

    def write(self, path, data, offset, fh):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print ("Path:{}" " " "data:{}" " " "offset:{}" " "  "filehandle{}".format(path,data,offset,fh))
        print('In function write()')
        
        self.FS.write_file(path, data, offset, fh)
        return len(data)

    def open(self, path, flags):
        global count
        count +=1
        print ("CallCount {} " " Time {}" " " "argumnets:" " " "path:{}" "," "flags:{}".format(count,datetime.datetime.now().time(),path,flags))
        print('In function open()')

        self.FS.fd += 1
        return  self.FS.fd 

    def read(self, path, size, offset, fh):
        global count
        count +=1
        print ("CallCount {} " " Time {}" " " "arguments:" " " "path:{}" "," "size:{}" "," "offset:{}" "," "fh:{}".format(count,datetime.datetime.now().time(),path,size,offset,fh))
        print('In function read()')

        return self.FS.read_file(path,offset,size)

    def rename(self, old, new):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function rename()')

        self.FS.rename_node(old,new)

    def utimens(self, path, times=None):
        global count
        count +=1
        print ("CallCount {} " " Time {} Path {}".format(count,datetime.datetime.now().time(),path))
        print('In function utimens()')

        self.FS.utimens(path,times)

    def rmdir(self, path):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function rmdir()')

        self.FS.delete_node(path)

    def unlink(self, path):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function unlink()')

        self.FS.delete_node(path)

    def symlink(self, target, source):
        global count
        count +=1
        print ("CallCount {} " " Time {}" "," "Target:{}" "," "Source:{}".format(count,datetime.datetime.now().time(),target,source))
        print('In function symlink()')

        self.FS.link_nodes(target,source)

    def readlink(self, path):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function readlink()')
        
        return self.FS.read_file(path)

    def truncate(self, path, length, fh=None):
        global count
        print ("CallCount {} " " Time {}""," "arguments:" "path:{}" "," "length:{}" "," "fh:{}".format(count,datetime.datetime.now().time(),path,length,fh))
        print('In function truncate()')
        
        self.FS.write_file(path,offset=length)

    def chmod(self, path, mode):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function chmod()')

        self.FS.update_meta(path,mode=mode)
        return 0

    def chown(self, path, uid, gid):
        global count
        count +=1
        print ("CallCount {} " " Time {}".format(count,datetime.datetime.now().time()))
        print('In function chown()')

        self.FS.update_meta(path,uid=uid,gid=gid)
        

if __name__ == '__main__':
  	if (len(argv) != (int(argv[3])+5)) and (argv[2] > argv[3]):
    		print 'usage: %s <mountpoint> <remote hashtable>' % argv[0]
    		exit(1)
  		#ports = argv[2]
	ports = []
  	ports = argv
	print ports
  	# Create a new HtProxy object using the ports specified at the command-line
  	fuse = FUSE(Memory(ports), argv[1], foreground=True)
