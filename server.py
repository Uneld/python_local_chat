#!/bin/python3
import socket
import threading

# Connection Data
HOST = '127.0.0.1'
PORT = 55555
BUFFER_SIZE = 1024

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

user_count = {}
count_client = 0

lock = threading.Lock()


def broadcast_with_nickname(message, nickname):
    with lock:
        # user_count[nickname] = nickname[nickname] + 1
        # print(user_count)
        for client in clients:
            nik = f"\"{nickname}\": ".encode('ascii')
            client.send(nik + message)


# Sending Messages To All Connected Clients
def broadcast(message):
    with lock:
        for client in clients:
            client.send(message)


# Handling Messages From Clients
def handle(client, nickname):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(BUFFER_SIZE)
            if message.decode('ascii') == "stats":
                message = f"All clients on server: {count_client}\n".encode('ascii')
                for key, value in user_count.items():
                    message += f"User: \"{key}\" msg={value}\n".encode('ascii')
                broadcast(message)
            else:
                user_count[nickname] = user_count[nickname] + 1
                print(user_count)
                broadcast_with_nickname(message, nickname)
        except:
            # Removing And Closing Clients
            with lock:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f'\"{nickname}\" left chat!\n'.encode('ascii'))
                nicknames.remove(nickname)
            break


# Receiving / Listening Function
def receive():
    global count_client
    while True:
        # Accept Connection
        client, address = server.accept()
        print(f"Connected with {address}")

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(BUFFER_SIZE).decode('ascii')
        with lock:
            nicknames.append(nickname)
            clients.append(client)

        # Print And Broadcast Nickname
        print(f"Nickname is {nickname}")
        client.send('Connected to server!\n'.encode('ascii'))
        broadcast(f"\"{nickname}\" joined to chat!\n".encode('ascii'))

        # Start Handling Thread For Client
        count_client += 1
        user_count[nickname] = 0
        print(user_count)
        thread = threading.Thread(target=handle, args=(client, nickname,))
        thread.start()


print("Server is listening...")
receive()
