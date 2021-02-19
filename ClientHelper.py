import select
import socket


def clients_read(r_clients, clientlist):
    responses = {}
    for sock in r_clients:
        try:
            data = sock.recv(1024).decode()
            responses[sock] = data
            print(data)
        except:
            print(f'Client {sock.fileno()}{sock.getpeername()} disconnected')
            clientlist.remove(sock)
    return responses


def clients_write(requests, w_clients, all_clients):
    for sock in w_clients:
        if sock in requests:
            try:
                response = requests[sock].encode()
                sock.send(response)
                print(response)
            except:
                print(f'Client {sock.fileno()}{sock.getpeername()} disconnected')
                sock.close()
                all_clients.remove(sock)

