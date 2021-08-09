# -*- coding: utf-8 -*-
#gzwuguangdong
import os
import sys
import time
import json
import urllib
import threading

import tornado.ioloop
import tornado.web

import _config
from common import log
from common import timer
from game.cmd import wizcmd_server
# from common import update
# from master.network import game_manager

g_tornado_thread = None

# g_qa_server = [45, 46, 65]

def Yielder():
	time.sleep(0.001)

def CallFunctionInMain(func, *args, **kwargs):
	timer.TimerOnce(0, func, "__call__", *args, **kwargs)

# def CallUpdate(module_name):
# 	update.Update(module_name)
# 	for game_me in game_manager.GetReadyMediators().itervalues():
# 		game_me.gen_server_cast.qc.UpdateModule(module_name)

def SaveUpdateFiles(update_files):
	dirname = './hotfix/server/'
	filename = "%s_internal.list" % (time.strftime("%Y%m%d_%H%M%S"))
	filepath = os.path.join(dirname, filename)
	f = open(filepath, "w")
	f.write("file_list = [\n")
	for name in update_files:
		f.write("'%s',\n" % name)
	f.write("]\n")
	f.close()


#热更新接口，需要根据自己项目实际调用方式进行修改
def UpdateFile(update_files):
	# from common import shell
	# shell.SaveUpdateFiles(update_files)
	SaveUpdateFiles(update_files)
	from common import auto_update
	auto_update.CheckUpdate()

def CallGameCmd(guid, cmd_str):
	wizcmd_server.UpdateAllGame('game.cmd.qccmd.qc_detail.qcauto_test', 'QcLet', guid, cmd_str)

class TestEcho(tornado.web.RequestHandler):
	def get(self):
		self.write("QaWebServer is running")

class UploadHandler(tornado.web.RequestHandler):
	def post(self):
		fileinfos = self.request.files['uploadfiles']
		static_path = "setting/staticdata/"
		datadir = os.path.abspath(os.path.join(os.getcwd(), static_path))
		try:
			update_files=[]
			for fileinfo in fileinfos:
				filename = fileinfo['filename']
				fullname = os.path.join(datadir,filename)
				with open(fullname, 'w') as fh:
					fh.write(fileinfo['body'])
				log.Trace("[QaWebServer]uploaded success","filename",filename)
				module_path=static_path+filename.replace(r"\\","/")
				update_files.append(module_path)
			#热更新模块
			CallFunctionInMain(UpdateFile, update_files)
			log.Trace("[QaWebServer]update success","update_files",update_files)
			self.write("success")
		except IOError as e:
			log.Trace("[QaWebServer]Failed to write file: %s", str(e))
			self.write("Failed to write file:"+str(e))

class ProcessCmd(tornado.web.RequestHandler):
	def get(self):
		guid = self.get_argument("guid", None)
		cmd_str = self.get_argument("cmd_str", None)
		if not guid:
			self.write("fail to load guid")
			return
		if not cmd_str:
			self.write("failt to load cmd")
			return
		CallFunctionInMain(CallGameCmd, int(guid), cmd_str)
		self.write("succese")

#检查log比较慢，用异步
class CheckError(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		log.Trace('get from url')


application = tornado.web.Application([
	(r"/test", TestEcho),
	(r"/uploadfile", UploadHandler),
	(r"/wizcmd", ProcessCmd),
	])

def __Start__():
	#window系统不需要开
	if sys.platform == "win32":
		return
	#只在game1开，避免重复。
	if _config.GetServerIndex()!=1:
		return
	#已经开启了不需要重复开
	global g_tornado_thread
	if g_tornado_thread is not None:
		return
	#获取服务器ip和id
	ip = _config.GetExternalIP()
	group_id = _config.GetServerGroupID()
	if group_id>100: #not in g_qa_server:
		return
	# 与ExcelTool约定端口尾号为99
	web_qa_port = 99
	# 端口为 1xx99，xx为服务器id
	port = 10000+group_id*100+web_qa_port
	# 必须注意线程安全性
	def start_tornado():
		application.listen(port, ip)
		tornado.ioloop.IOLoop.instance().start()
	g_tornado_thread = threading.Thread(target = start_tornado)
	g_tornado_thread.start()
	timer.TimerPersist(0.01, Yielder, "__call__")#定时触发一次线程调度，让web服务线程更有机会调度到
	log.Trace("[QaWebServer]Start qa web", "ip", ip, "port", port)


def __Stop__():
	if sys.platform == "win32":
		return
	if _config.GetServerIndex()!=1:
		return
	global g_tornado_thread
	if g_tornado_thread is None:
		return
	log.Trace("[QaWebServer]Stop qa web")
	def stop_tornado():
		tornado.ioloop.IOLoop.instance().stop()
	tornado.ioloop.IOLoop.instance().add_callback(stop_tornado)
