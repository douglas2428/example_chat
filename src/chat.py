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

class ChatConnection(SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()
    users=dict()
    room_by_user=dict()

    def on_open(self, info):
        # Send that someone joined
        """
        self.send_text("System","Someone joined.")
        
        self.participants.add(self)"""

    def on_message(self, message):

        print self

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
        room = get_room(data['lat'], data['lon'])
        
        if room != None and not [key for key in self.users.keys() if self.users[key] == data['username']]:
            self.users[self]=data['username']


            print data['lat'], data['lon']
            print "Entrara a:"
            print room

            data={'username':data['username'],'isAvailable':True,'room':room}
            self.send_text("System",data['username']+" has joined")
        else:
            data={'username':data['username'],'isAvailable':False,'room':room}    
            
        self.participants.add(self)
        self.send(json.dumps({'data_type': 'auth', 'data': data}))        
         
    #  NO sockjs functions      
    def get_room(lat, lon):
        try:
            lat, lon = int(float(lat)*100)/100.0, int(float(lon)*100)/100.0

            return "lat:{0:.2f},{1:.2f}|lon:{2:.2f},{3:.2f}".format(lat+0.01, lat, lon+0.01, lon)
        except Exception as e:
            print str(e)
            return None            

    def join_room(username, room):
        pass
        #room_by_user[]

    def leave_room(username):
        pass

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