# -*- coding: utf-8 -*-
"""
    Simple sockjs-tornado chat application. By default will listen on port 8080.
"""
import os.path
import tornado.ioloop
import tornado.web
from sockjs.tornado import SockJSRouter,SockJSConnection
import sys
import json

PATH_ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),os.pardir))

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')

inc=int(0)
class ChatConnection(SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()
    users=dict()
    def on_open(self, info):
        # Send that someone joined
        """
        self.send_text("System","Someone joined.")
        
        self.participants.add(self)"""

    def on_message(self, message):
        msg = json.loads(message)
        data_type = msg['data_type']
        data=msg['data']


        if data_type=="send_text":
            self.send_text(self.users[self],data)
        elif data_type=="auth":
            self.authenticate(data)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)
        username=self.users[self]
        del self.users[self]
        self.send_text("System",username+" left.")

    def send_text(self,name_from,text):
        data={'username':name_from,'text':text}
        self.broadcast(self.participants, json.dumps({'data_type': 'send_text', 'data': data}))     

    def authenticate(self,data):
        if not [key for key in self.users.keys() if self.users[key] == data['username']]:
            self.users[self]=data['username']
            data={'username':data['username'],'isAvailable':True}
            self.send_text("System",data['username']+" has joined")
        else:
            data={'username':data['username'],'isAvailable':False}    
            
        self.participants.add(self)
        self.send(json.dumps({'data_type': 'auth', 'data': data}))        
        
            

def main():

    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create chat router
    ChatRouter = SockJSRouter(ChatConnection, '/chat')

    # 2. Create Tornado application
    app = tornado.web.Application(
            [(r"/", IndexHandler)] + ChatRouter.urls,
    template_path=os.path.join(PATH_ROOT, 'example_chat/templates'),
    static_path=os.path.join(PATH_ROOT, 'example_chat/static'),        
    )

    # 3. Make Tornado app listen on port 8080
    app.listen(8080)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()    