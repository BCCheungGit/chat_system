import socket
import time

# use local loop back address by default
# CHAT_IP = '155.138.134.163'
# CHAT_IP = socket.gethostbyname(socket.gethostname())
CHAT_IP = socket.gethostbyname(socket.gethostname())

CHAT_PORT = 1112
SERVER = (CHAT_IP, CHAT_PORT)

menu = "\n++++ Choose one of the following commands\n \
        time: calendar time in the system\n \
        who: to find out who else are there\n \
        c _peer_: to connect to the _peer_ and chat\n \
        g : play a game of tic-tac-toe\n \
        ? _term_: to search your chat logs where _term_ appears\n \
        p _#_: to get number <#> sonnet\n \
        b _message_: to send a message to an AI \n \
        (This may take a while due to the api's latency)\n  \
        q: to leave the chat system\n\n"

S_OFFLINE = 0
S_CONNECTED = 1
S_LOGGEDIN = 2
S_CHATTING = 3
S_BOT = 4
S_GAME = 6

SIZE_SPEC = 5

CHAT_WAIT = 0.2


def print_state(state):
    print("**** State *****::::: ")
    if state == S_OFFLINE:
        print("Offline")
    elif state == S_CONNECTED:
        print("Connected")
    elif state == S_LOGGEDIN:
        print("Logged in")
    elif state == S_GAME:
        print("Playing mini game")
    elif state == S_CHATTING:
        print("Chatting")
    else:
        print("Error: wrong state")


def mysend(s, msg):
    # append size to message and send it
    msg = ("0" * SIZE_SPEC + str(len(msg)))[-SIZE_SPEC:] + str(msg)
    msg = msg.encode()
    total_sent = 0
    while total_sent < len(msg):
        sent = s.send(msg[total_sent:])
        if sent == 0:
            print("server disconnected")
            break
        total_sent += sent


def myrecv(s):
    # receive size first
    size = ""
    while len(size) < SIZE_SPEC:
        text = s.recv(SIZE_SPEC - len(size)).decode()
        if not text:
            print("disconnected")
            return ""
        size += text
    size = int(size)
    # now receive message
    msg = ""
    while len(msg) < size:
        text = s.recv(size - len(msg)).decode()
        if text == b"":
            print("disconnected")
            break
        msg += text
    # print ('received '+message)
    return msg


def text_proc(text, user):
    ctime = time.strftime("%d.%m.%y,%H:%M", time.localtime())
    return "(" + ctime + ") " + user + " : " + text  # message goes directly to screen


# pretty print a tic-tac-toe board
def print_board(
    board=[
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
):
    result = ""
    result += "   0   1   2\n"
    result += (
        "a  "
        + (str(board[0][0]) if board[0][0] is not None else "  ")
        + " | "
        + (str(board[0][1]) if board[0][1] is not None else "  ")
        + " | "
        + (str(board[0][2]) if board[0][2] is not None else "  ")
        + "\n"
    )
    result += "  ---+---+---\n"
    result += (
        "b  "
        + (str(board[1][0]) if board[1][0] is not None else "  ")
        + " | "
        + (str(board[1][1]) if board[1][1] is not None else "  ")
        + " | "
        + (str(board[1][2]) if board[1][2] is not None else "  ")
        + "\n"
    )
    result += "  ---+---+---\n"
    result += (
        "c  "
        + (str(board[2][0]) if board[2][0] is not None else "  ")
        + " | "
        + (str(board[2][1]) if board[2][1] is not None else "  ")
        + " | "
        + (str(board[2][2]) if board[2][2] is not None else "  ")
        + "\n"
    )

    return result
