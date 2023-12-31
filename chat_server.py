"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""
import os
import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
from tic_tac_toe import *
import chat_group as grp

import requests

url = "https://robomatic-ai.p.rapidapi.com/api"


class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        # self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        # self.sonnet = pkl.load(self.sonnet_f)
        # self.sonnet_f.close()
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.game_state = {}

    def new_client(self, sock):
        # add to all sockets and to new clients
        print("new client...")
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def save_user_info(self, name, password):
        self.indices[name] = indexer.Index(name, password)
        with open("Users/" + name + ".idx", "wb") as f:
            pkl.dump(self.indices[name], f)

    def check_user_info(self, name):
        try:
            with open("Users/" + name + ".idx", "rb") as f:
                try:
                    pkl.load(f)
                    return True
                except EOFError:
                    return False
        except IOError:
            return False

    def check_password(self, name, password):
        try:
            with open("Users/" + name + ".idx", "rb") as f:
                try:
                    user = pkl.load(f)
                    if user.password == password:
                        return True
                    else:
                        return False
                except EOFError:
                    return False
        except IOError:
            return False

    def auth(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:
                if msg["action"] == "register":
                    name = msg["name"]
                    password = msg["password"]
                    password2 = msg["password2"]
                    if password != password2:
                        mysend(
                            sock,
                            json.dumps(
                                {"action": "register", "status": "mismatched passwords"}
                            ),
                        )
                    elif self.check_user_info(name):
                        mysend(
                            sock,
                            json.dumps(
                                {"action": "register", "status": "duplicate username"}
                            ),
                        )
                    else:
                        self.save_user_info(name, password)
                        mysend(sock, json.dumps({"action": "register", "status": "ok"}))

                elif msg["action"] == "login":
                    name = msg["name"]
                    password = msg["password"]
                    if self.check_user_info(name) == False:
                        mysend(
                            sock,
                            json.dumps(
                                {
                                    "action": "login",
                                    "status": "User does not exist, please register",
                                }
                            ),
                        )
                    elif self.check_password(name, password):
                        if self.group.is_member(name) != True:
                            # move socket from new clients list to logged clients
                            self.new_clients.remove(sock)
                            # add into the name to sock mapping
                            self.logged_name2sock[name] = sock
                            self.logged_sock2name[sock] = name
                            # load chat history of that user
                            if name not in self.indices.keys():
                                try:
                                    self.indices[name] = pkl.load(
                                        open(name + ".idx", "rb")
                                    )
                                except (
                                    IOError
                                ):  # chat index does not exist, then create one
                                    self.indices[name] = indexer.Index(name, None)
                            print(name + " logged in")
                            self.group.join(name)
                            mysend(
                                sock, json.dumps({"action": "login", "status": "ok"})
                            )

                        else:  # a client under this name has already logged in
                            mysend(
                                sock,
                                json.dumps({"action": "login", "status": "duplicate"}),
                            )
                            print(name + " duplicate login attempt")
                    else:
                        mysend(
                            sock,
                            json.dumps({"action": "login", "status": "wrong password"}),
                        )
                else:
                    print("wrong code received")
            else:  # client died unexpectedly
                print("client died...")
                self.logout(sock)
        except:
            print("no message received...")
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        # pkl.dump(self.indices[name], open("Users/" + name + '.idx','wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

    # ==============================================================================
    # main command switchboard
    # ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps({"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(
                            to_sock,
                            json.dumps(
                                {
                                    "action": "connect",
                                    "status": "request",
                                    "from": from_name,
                                }
                            ),
                        )
                else:
                    msg = json.dumps({"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)
            # ==============================================================================
            # handle messeage exchange: one peer for now. will need multicast later
            # ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                # said = msg["from"]+msg["message"]
                said2 = text_proc(msg["message"], from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(said2)
                    mysend(
                        to_sock,
                        json.dumps(
                            {
                                "action": "exchange",
                                "from": msg["from"],
                                "message": msg["message"],
                            }
                        ),
                    )

            elif msg["action"] == "connect_to_game":
                from_name = self.logged_sock2name[from_sock]
                self.game_state[from_name] = [
                    [" ", " ", " "],
                    [" ", " ", " "],
                    [" ", " ", " "],
                ]
                print(from_name + " connected to game")
                msg = json.dumps(
                    {
                        "action": "connect_to_game",
                        "status": "success",
                    }
                )
                mysend(from_sock, msg)

            elif msg["action"] == "make_move":
                from_name = self.logged_sock2name[from_sock]
                move = msg["move"]
                row = ord(move[0].lower()) - ord("a")
                col = int(move[1])
                if self.game_state[from_name][row][col] != " ":
                    msg = json.dumps(
                        {
                            "action": "make_move",
                            "status": "invalid",
                        }
                    )
                    mysend(from_sock, msg)
                    return
                self.game_state[from_name][row][col] = "X"
                comp_move = getAIMove(sum(self.game_state[from_name], []), "O", "O")
                if comp_move[0] != -1:
                    self.game_state[from_name][comp_move[0] // 3][
                        comp_move[0] % 3
                    ] = "O"
                if checkWin(sum(self.game_state[from_name], []), "X"):
                    msg = json.dumps(
                        {
                            "action": "make_move",
                            "status": "win",
                            "board": self.game_state[from_name],
                        }
                    )
                    mysend(from_sock, msg)
                    return
                elif checkLose(sum(self.game_state[from_name], []), "X"):
                    msg = json.dumps(
                        {
                            "action": "make_move",
                            "status": "lose",
                            "board": self.game_state[from_name],
                        }
                    )
                    mysend(from_sock, msg)
                    return
                elif checkTie(sum(self.game_state[from_name], [])):
                    msg = json.dumps(
                        {
                            "action": "make_move",
                            "status": "tie",
                            "board": self.game_state[from_name],
                        }
                    )
                    mysend(from_sock, msg)
                    return
                msg = json.dumps(
                    {
                        "action": "make_move",
                        "status": "success",
                        "board": self.game_state[from_name],
                    }
                )
                mysend(from_sock, msg)

            # ==============================================================================
            #                 listing available peers
            # ==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all()
                mysend(from_sock, json.dumps({"action": "list", "results": msg}))
            # ==============================================================================
            #             Talk to AI Chatbot
            # ==============================================================================
            elif msg["action"] == "bot":
                message = msg["message"]
                payload = {
                    "in": message,
                    "op": "in",
                    "cbot": "1",
                    "SesionId": "RapidAPI1",
                    "cbid": "1",
                    "key": "RHMN5hnQ4wTYZBGCF3dfxzypt68rVP",
                    "ChatSource": "RapidAPI",
                    "duration": "1",
                }
                headers = {
                    "content-type": "application/x-www-form-urlencoded",
                    "X-RapidAPI-Key": "08221f0e07msh9ce2a8ae74c15fbp16a631jsn675a3a8e5553",
                    "X-RapidAPI-Host": "robomatic-ai.p.rapidapi.com",
                }
                response = requests.post(url, data=payload, headers=headers)
                mysend(
                    from_sock,
                    json.dumps({"action": "bot", "results": response.json()["out"]}),
                )

            # ==============================================================================
            #             retrieve a sonnet
            # ==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + " asks for ", poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = "\n".join(poem).strip()
                print("here:\n", poem)
                mysend(from_sock, json.dumps({"action": "poem", "results": poem}))
            # ==============================================================================
            #                 time
            # ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime("%d.%m.%y,%H:%M", time.localtime())
                mysend(from_sock, json.dumps({"action": "time", "results": ctime}))
            # ==============================================================================
            #                 search
            # ==============================================================================
            elif msg["action"] == "search":
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print("search for " + from_name + " for " + term)
                # search_rslt = (self.indices[from_name].search(term))
                search_rslt = "\n".join(
                    [x[-1] for x in self.indices[from_name].search(term)]
                )
                print("server side search: " + search_rslt)
                mysend(
                    from_sock, json.dumps({"action": "search", "results": search_rslt})
                )
            # ==============================================================================
            # the "from" guy has had enough (talking to "to")!
            # ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action": "disconnect"}))
        # ==============================================================================
        #                 the "from" guy really, really has had enough
        # ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

    # ==============================================================================
    # main loop, loops *forever*
    # ==============================================================================
    def run(self):
        print("starting server...")
        while 1:
            read, write, error = select.select(self.all_sockets, [], [])
            print("checking logged clients..")
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print("checking new clients..")
            for newc in self.new_clients[:]:
                if newc in read:
                    self.auth(newc)
            print("checking for new connections..")
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


main()
