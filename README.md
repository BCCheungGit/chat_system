# Chat system
This is the final project for ICSDS @ NYU Shanghai, a chat system with GUI and Pygame. 

Authors: Ben Cheung bc3431, Leo Wang rw3232.

## Running the chat system
First, set up a python virtual env (I use venv and git bash):

```
python -m venv venv
```

Then, activate venv:

```
source venv/Scripts/activate
```

to start the python virutal env.

Then, run:

```
pip install -r requirements.txt
```

to install required packages.

-----------------------------------

To run the chat server, run:

```
python chat_server.py
```

Finally, open an instance of the client with:

```
python chat_cmdl_client.py
```

## Current Features:
- [x] login and register pages, storing user data
- [x] talk to a chatbot using RapidAPI and robomatic AI: [More Info](https://robomatic.ai/)
- [ ] light and dark mode with toggle button
- [x] text-based tic-tac-toe game

## GUI TODO
- [x] add login and sign up page
- [x] messages always display on new line
- [x] talk with a chatbot using RapidAPI
- [ ] light and dark mode with toggle button

