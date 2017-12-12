import socket, sys
from common import recv_all


def client(HOST, PORT):
    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError:
            s = None
            print('socket() failed')
            continue

        try:
            s.connect((HOST, PORT))
        except OSError:
            s.close()
            s = None
            print('connect failed')
            continue
        break

    if s is None:
        print('could not open socket')
        sys.exit(1)
    msg = input('Please enter your message: ')
    # determine the message length (max 255 characters, i.e. 3 digits), pad with leading zeroes
    msg_length_in_str = str(len(msg))
    msg_length_in_str = msg_length_in_str.zfill(3)

    s.sendall(msg_length_in_str + msg)  # add the length at the beginning of the message
    reply = recv_all(s, 3)
    print('Server:', repr(reply))
    s.close()
