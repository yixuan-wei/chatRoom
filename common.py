import socket, sys


def recv_all(sock,length):
    raw = b''

    while len(raw)<length:
        more = sock.recv(length-len(raw))
        if not more:
            raise EOFError('socket closed when receiving head info')
        raw += more
    return str(raw, encoding='utf8')


