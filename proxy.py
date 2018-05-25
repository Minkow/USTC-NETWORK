#coding=utf-8

import socket
import threading
import BaseHTTPServer
import urllib2
from SocketServer import ThreadingMixIn

BUFFER_SIZE = 1024

class Handle(BaseHTTPServer.BaseHTTPRequestHandler):
    def respon(self,ret):
        req={}
        req['method']=self.command
        req['url']=self.path
        req['headers']=dict(self.headers)
        #读请求，格式为COMMAND PATH VERSION\r\n
        res={}
        res['code'] = ret.getcode()
        res['headers'] = dict(ret.headers)
        #写回复
        self.send_response(ret.getcode())
        for key in ret.headers.keys():
            self.send_header(key,ret.headers[key])
        self.end_headers()
        #写header
        data={'request':req,'response':res,'suc':0}
        data=ret.read(BUFFER_SIZE)
        while data:
            self.wfile.write(data)
            data=ret.read(BUFFER_SIZE)
        #写data
            
#以下为request请求的判断(get/post/https)
    def do_GET(self):
        print self.raw_requestline
        try:
            request=urllib2.Request(self.path,headers=self.headers) #源地址作为request
            if "csdn.net" in self.path:
                request.add_header('', '')
            #此处：判断csdn.net是否出现在url中(我们注意到csdn并没有用https)，有则给header添加神秘代码，使其无法发送请求
            response=urllib2.urlopen(request) #写request头
        except urllib2.HTTPError,e:
            response=e
        self.respon(response)

    def do_POST(self):
        content_length=int(self.headers['content-length'])
        data=self.rfile.read(content_length)
        try:
            request=urllib2.Request(self.path,data,headers=self.headers)
            if "csdn.net" in self.path:
                request.add_header('', '')
            #此处：判断csdn.net是否出现在url中(我们注意到csdn并            没有用https)，有则给header添加神秘代码，使其无法发送请求
            response=urllib2.urlopen(request)
        except urllib2.HTTPError,e:
            response=e
        self.respon(response)

    def do_CONNECT(self):  #https:先向代理发送CONNECT的request,代理向server建立连接后，再由代理给client回送报文
        print self.protocol_version
        self.send_response(200)
        self.end_headers()
        s0=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host,port=self.path.split(':')
        port=int(port)
        print self.raw_requestline
        s0.connect((host,port))
        s0_fd=s0.makefile('rw',0)
        t1=threading.Thread(target=self.https,args=(self.connection,s0))
        t2=threading.Thread(target=self.https,args=(s0,self.connection))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        #需要两个进程已完成上述功能

    def https(self,s1,s2):  #用于https的函数
        data=s1.recv(BUFFER_SIZE)
        while data:
            s2.sendall(data)
            data=s1.recv(BUFFER_SIZE)

class ThreadHttpServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass
#一个进程被生成时创建新进程

class RedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        pass
    def http_error_303(self, req, fp, code, msg, headers):
        pass
    def http_error_304(self, req, fp, code, msg, headers):
        pass
    def http_error_305(self, req, fp, code, msg, headers):
        pass
    def http_error_306(self, req, fp, code, msg, headers):
        pass    
    def http_error_307(self, req, fp, code, msg, headers):
        pass
    def http_error_300(self, req, fp, code, msg, headers):
        pass

#需要取消3xx状态的redirect
urllib2.install_opener(urllib2.build_opener(RedirectHandler))

if __name__ == '__main__':
    server = ThreadHttpServer(('127.0.0.1',1234),Handle) #localhost 端口=1234
    server.serve_forever()    