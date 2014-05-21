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
    participants = dict()
    users = dict()
    room_by_user = dict()

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
            self.send_text(self.users[self], self.room_by_user[username], data)
        elif data_type=="auth":
            self.authenticate(data)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.leave_room(self)
        
    def send_text(self, name_from, room, text):
        data={'username':name_from,'text':text}
        self.broadcast(self.participants[room], json.dumps({'data_type': 'send_text', 'data': data}))     

    def authenticate(self, data):
        room = self.get_room(data['lat'], data['lon'])
        
        print data['username'], "Entrara a:"
        print data['lat'], data['lon']
        print room

        self.join_room(self, data['username'], room)
         

    def join_room(self, client, username, room):
        if room != None and not [key for key in self.users.keys() if self.users[key] == username]:
            self.users[client]=username
            self.room_by_user[username] = room
            
            if room not in self.participants:
                self.participants[room] = set()
            self.participants[room].add(client)
        
            data={'username':username,'isAvailable':True,'room':room}
            self.send_text("System", room, username+" has joined")
        else:
            data={'username':username,'isAvailable':False,'room':room}    
            
        self.send(json.dumps({'data_type': 'auth', 'data': data}))



    #  NO sockjs functions      
    def get_room(self, lat, lon):
        try:
            lat, lon = int(float(lat)*100)/100.0, int(float(lon)*100)/100.0

            return "lat:{0:.2f},{1:.2f}|lon:{2:.2f},{3:.2f}".format(lat+0.01, lat, lon+0.01, lon)
        except Exception as e:
            print str(e)
            return None        

    def leave_room(self, client):
        username = self.users[client]
        room = self.room_by_user[username]

        self.participants[room].remove(client)
        del self.users[client]

        self.send_text("System", room, username+" left.")


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