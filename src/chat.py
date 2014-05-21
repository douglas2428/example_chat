# -*- coding: utf-8 -*-
"""
    Simple sockjs-tornado chat application. By default will listen on port 8080.
"""
import os.path
import tornado.ioloop
import tornado.web
import sys
import json
from sockjs.tornado import SockJSRouter
from sockjs.tornado import SockJSConnection

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

        if data_type=="send_text":
            target = msg['target'] if 'target' in msg else None
            self.send_text(self.users[self], self.room_by_user[self.users[self]], msg['data'], target)
        elif data_type=="auth":
            self.authenticate(msg['data'])
        elif data_type=="change_location":
            self.change_room(self, msg)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.leave_room(self)
        
    def send_text(self, username, room, text, target=None):
        data={'username':username,'text':text}

        is_private = target!=None
        target = [user for user in self.participants[room] if self.users[user] in (target, username)] if target else self.participants[room]

        self.broadcast(target, json.dumps({'data_type': 'send_text', 'data': data, 'private':is_private}))     

    def send_list_users(self, room):
        data = [self.users[user] for user in self.participants[room]]
        self.broadcast(self.participants[room], json.dumps({'data_type': 'send_list_users', 'data': data}))     

    def authenticate(self, data):
        room = self.get_room(data['lat'], data['lon'])
        self.join_room(self, data['username'], room)

    #  NO sockjs functions      
    def get_room(self, lat, lon):
        try:
            lat, lon = int(float(lat)*100)/100.0, int(float(lon)*100)/100.0

            return "lat:{0:.2f},{1:.2f}|lon:{2:.2f},{3:.2f}".format(lat+0.01, lat, lon+0.01, lon)
        except Exception as e:
            print str(e)
            return None        

    def join_room(self, client, username, room):
        
        if room != None and not [key for key in self.users.keys() if self.users[key] == username]:
            self.users[client]=username
            self.room_by_user[username] = room
            
            if room not in self.participants:
                self.participants[room] = set()
            self.participants[room].add(client)
            
            self.send_list_users(room)
            
            data={'username':username,'isAvailable':True,'room':room}
            self.send_text("System", room, username+" has joined")
        else:
            data={'username':username,'isAvailable':False,'room':room}    
            
        self.send(json.dumps({'data_type': 'auth', 'data': data}))

    def leave_room(self, client):
        username = self.users[client]
        room = self.room_by_user[username]

        self.participants[room].remove(client)
        del self.users[client]

        self.send_list_users(room)

        self.send_text("System", room, username+" left.")

    def change_room(self, client, data):
        username = self.users[client]
        room = self.get_room(data['lat'], data['lon'])

        self.leave_room(client)

        self.join_room(client, username, room)


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