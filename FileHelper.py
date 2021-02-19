import struct

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
    file = open(filename, 'rb').read()
    msg = struct.pack('>I', len(file)) + file
    sock.send(msg)


def file_upload(sock, filepath):  # from server to client
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Получение данных
    file = recvall(sock, msglen)
    with open(filepath, 'wb') as created_file:
        try:
            created_file.write(file)
            confirm_text = 'Uploaded file saved to ' + filepath
            sock.send(confirm_text.encode())
        except:
            error_text = 'Upload error'
            sock.send(error_text.encode())