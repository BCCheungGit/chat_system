
import threading
import select
from tkinter import *
from tkinter import messagebox
from chat_utils import *
import json

# GUI class for the chat
class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""

    def go_register(self):
        self.register = Toplevel()
        self.register.title("Register")
        self.register.resizable(width=False, height=False)
        self.register.configure(width=400, height=300)
        self.pls = Label(self.register, text="Are you new? Register here", justify=CENTER, font="Helvetica 14 bold")
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)
        
        self.labelrName = Label(self.register, text="Name: ", font="Helvetica 12")
        self.labelrName.place(relheight=0.2, relx=0.1, rely=0.2)
        self.entryrName = Entry(self.register, font="Helvetica 14")
        self.entryrName.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.2)
        self.entryrName.focus()
        
        
        self.labelrPass = Label(self.register, text="Password: ", font="Helvetica 12")
        self.labelrPass.place(relheight=0.2, relx=0.1, rely=0.35)
        self.entryrPass = Entry(self.register, font="Helvetica 14", show="*")
        self.entryrPass.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.35)
        
        
        self.labelrPass2 = Label(self.register, text="Confirm Password: ", font="Helvetica 8")
        self.labelrPass2.place(relheight=0.2, relx=0.1, rely=0.5)
        self.entryrPass2 = Entry(self.register, font="Helvetica 14", show="*")
        self.entryrPass2.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.5)
        self.rgo = Button(self.register, text="CONTINUE", font="Helvetica 14 bold", command=lambda: self.handleRegister(self.entryrName.get(), self.entryrPass.get(), self.entryrPass2.get()))
        self.rgo.place(relx=0.4, rely=0.65)
    
    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width = False, 
                             height = False)
        self.login.configure(width = 400,
                             height = 300)
        # create a Label
        self.pls = Label(self.login, 
                       text = "Please login to continue",
                       justify = CENTER, 
                       font = "Helvetica 14 bold")
          
        self.pls.place(relheight = 0.15,
                       relx = 0.2, 
                       rely = 0.07)
        # create a Label
        self.labelName = Label(self.login,
                               text = "Username: ",
                               font = "Helvetica 12")
          
        self.labelName.place(relheight = 0.2,
                             relx = 0.1, 
                             rely = 0.2)
          
        # create a entry box for 
        # tyoing the message
        self.entryName = Entry(self.login, 
                             font = "Helvetica 14")
          
        self.entryName.place(relwidth = 0.4, 
                             relheight = 0.12,
                             relx = 0.35,
                             rely = 0.2)
          
        # set the focus of the curser
        self.entryName.focus()
        
        self.labelPass = Label(self.login, text="Password: ", font="Helvetica 12")
        self.labelPass.place(relheight=0.2, relx=0.1, rely=0.35)
        
        self.entryPass = Entry(self.login, font="Helvetica 14", show="*")
        self.entryPass.place(relwidth=0.4, relheight=0.12, relx=0.35, rely=0.35)
                
        # create a Continue Button 
        # along with action
        self.go = Button(self.login,
                         text = "Login", 
                         font = "Helvetica 14 bold", 
                         command = lambda: self.handleLogin(self.entryName.get(), self.entryPass.get()))
          
        self.go.place(relx = 0.4,
                      rely = 0.55)
        
        self.register = Button(self.login, text="Register", font="Helvetica 14 bold", command=self.go_register)
        self.register.place(relx = 0.4,
                      rely = 0.75)
        


    
    def handleRegister(self, name, password, password2):
        if len(name) > 0 and len(password) > 0 and len(password2) > 0:
            msg = json.dumps({"action":"register", "name": name, "password": password, "password2": password2})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                messagebox.showinfo("info", "register success")
                self.entryrName.delete(0, END)
                self.entryrPass.delete(0, END)
                self.entryrPass2.delete(0, END)
                self.register.withdraw()       
            else:
                messagebox.showerror("error", response["status"])
        else:
            messagebox.showerror("error", "please fill in all fields")
            
    def handleLogin(self, name, password):
        if len(name) > 0 and len(password) > 0:
            msg = json.dumps({"action":"login", "name": name, "password": password})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                self.layout(name)
                self.textCons.config(state = NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")   
                self.textCons.insert(END, menu +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)
                # while True:
                #     self.proc()
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()
            else:   
                messagebox.showerror("error", response["status"])
                self.entryName.delete(0, END)
                self.entryPass.delete(0, END)
        else:
            messagebox.showerror("error", "please fill in all fields")
            self.entryName.delete(0, END)
            self.entryPass.delete(0, END)
            
            
    def bind_enter_key(self):
        if self.sm.get_state() == S_LOGGEDIN:
            self.entryMsg.bind("<Return>", lambda event: self.sendButton(self.entryMsg.get()))
            
 
    # The main layout of the chat
    def layout(self,name):
        
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width = False,
                              height = False)
        self.Window.configure(width = 470,
                              height = 550,
                              bg = "#17202A")
        self.labelHead = Label(self.Window,
                             bg = "#17202A", 
                              fg = "#EAECEE",
                              text = self.name ,
                               font = "Helvetica 13 bold",
                               pady = 5)
          
        self.labelHead.place(relwidth = 1)
        self.line = Label(self.Window,
                          width = 450,
                          bg = "#ABB2B9")
          
        self.line.place(relwidth = 1,
                        rely = 0.07,
                        relheight = 0.012)
          
        self.textCons = Text(self.Window,
                             width = 20, 
                             height = 2,
                             bg = "#17202A",
                             fg = "#EAECEE",
                             font = "Helvetica 14", 
                             padx = 5,
                             wrap="word",
                             pady = 5)
          
        self.textCons.place(relheight = 0.745,
                            relwidth = 1, 
                            rely = 0.08)
          
        self.labelBottom = Label(self.Window,
                                 bg = "#ABB2B9",
                                 height = 80)
          
        self.labelBottom.place(relwidth = 1,
                               rely = 0.825)
          
        self.entryMsg = Entry(self.labelBottom,
                              bg = "#2C3E50",
                              fg = "#EAECEE",
                              font = "Helvetica 13")
        self.bind_enter_key()  
        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth = 0.74,
                            relheight = 0.06,
                            rely = 0.008,
                            relx = 0.011)
          
        self.entryMsg.focus()
          
        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text = "Send",
                                font = "Helvetica 10 bold", 
                                width = 20,
                                bg = "#ABB2B9",
                                command = lambda : self.sendButton(self.entryMsg.get()))
          
        self.buttonMsg.place(relx = 0.77,
                             rely = 0.008,
                             relheight = 0.06, 
                             relwidth = 0.22)
          
        self.textCons.config(cursor = "arrow")
          
        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)
          
        # place the scroll bar 
        # into the gui window
        scrollbar.place(relheight = 1,
                        relx = 0.974)
          
        scrollbar.config(command = self.textCons.yview)
          
        self.textCons.config(state = DISABLED)
  
    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state = DISABLED)
        self.my_msg = msg
        # print(msg)
        self.entryMsg.delete(0, END)

    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg += self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state = NORMAL)
                self.textCons.insert(END, self.system_msg +"\n\n")      
                self.textCons.config(state = DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()
        self.Window.mainloop()
# create a GUI class object
if __name__ == "__main__": 
    g = GUI()
