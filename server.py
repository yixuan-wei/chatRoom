import socket, sys
from common import recv_all


def server(HOST, PORT):
    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError:
            s = None
            print('socket() failed')
            continue
            # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(sa)
            s.listen(1)
        except OSError:
            s.close()
            s = None
            continue
        break
    if s is None:
        print('could not open socket')
        sys.exit(1)
    while True:
        print('Listening at', s.getsockname())
        sc, sockname = s.accept()  # wait here until there is a request
        # get the length of the message first
        msg_length = int(recv_all(sc, 12))
        # get the 'real' message with proper length
        message = recv_all(sc, msg_length)
        print('Client said: ', message)
        sc.sendall(bytes('Bye',encoding='utf8'))
        sc.close()
