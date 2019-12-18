import sys
import random
import socket
import struct
from math import gcd
from threading import Thread
import argparse
import time
import concurrent.futures


class CheckPrime:
    result = False

    def __init__(self, n, maxtr=5):
        self.result = self.ss_test(n, maxtr)

    def get_a(self, n):
        a = random.randrange(2, n - 2, 1)
        # print(get_gdc(n, a)) #debug
        while gcd(n, a) != 1:
            # print("GDC not 1: ",  get_gdc(n, a), " a : ", a)
            return -1
            # a = random.randrange(2, n - 2, 1)
        return a

    def jacoby(self, a, n):
        if a == 0:
            return 0
        if a == 1:
            return 1

        k = 0
        s = 2

        while a % 2 == 0:
            k += 1
            a //= 2

        if k % 2 == 0:
            s = 1
        else:
            if n % 8 == 1 or n % 8 == 7:
                s = 1
            else:
                s = -1

        if a % 4 == 3 and n % 4 == 3:
            s = -s
        n = n % a
        if a == 1:
            return s
        else:
            return s * self.jacoby(n, a)

    def solovay_shtrassen(self, a, n):
        r = pow(a, (n - 1) // 2, n)
        if r != 1 and r != n - 1:
            return False

        s = self.jacoby(a, n)
        if s == -1:
            s = n - 1

        if r % n != s:
            return False
        else:
            return True

    def ss_test(self, n, maxtr=5):
        tr = 0
        a = self.get_a(n)
        while a == -1:
            a = self.get_a(n)
        while tr < maxtr and self.solovay_shtrassen(a, n):
            # print("a = ", a, " n is probably prime")
            if (tr % (maxtr / 5) == 0):
                pass
                # print("try", tr, " a = ", a, " n is probably prime")
            a = self.get_a(n)
            while a == -1:
                # print(" n is composite, GDC is not 1")
                # a = get_a(n)
                # return time.time() - tm
                return False
            tr = tr + 1
        if tr < maxtr:
            return False
            # print("a = ", a, " n is composite. Find on ", tr, " try")
        # print("=====================")
        return True

    def get_answ(self):
        return self.result


class MySocket:
    def __init__(self, sock):
        self.sock = sock

    def send_msg(self, msg):
        self.sock.send(struct.pack('>I', len(msg)) + bytes(msg, encoding='utf8'))

    def recv_msg(self):
        msglen = self.recvall(4)
        if not msglen:
            return None
        msglen = struct.unpack('>I', msglen)[0]
        return self.recvall(msglen)

    def recvall(self, n):
        data = b''
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data


def proc_client(conn, addr):
    while True:
        result = ""
        connection = MySocket(conn)
        border = connection.recv_msg().decode('utf-8')
        low = int(border.split(' ')[0])
        up = int(border.split(' ')[1])
        if low < 3 and up > 1:
            result = result + "2 "
        if low < 4 and up > 2:
            result = result + "3 "
        if low % 2 == 0:
            low = low + 1
        for p in range(low, up + 1, 2):
            if CheckPrime(p, 10).get_answ():
                result = result + str(p) + " "

        result = result[0: -1]
        connection.send_msg(result)
        conn.close()


def serv_proc(port=31337):
    print("Listening on port " + str(port))
    sock = socket.socket()
    sock.bind(('', port))
    sock.listen(10)
    while True:
        conn, addr = sock.accept()
        Thread(target=proc_client, args=(conn, addr)).start()


def cli_thread(address, port, low, high):
    sock = socket.socket()
    sock.connect((address, port))
    connection = MySocket(sock)
    msg = str(low) + " " + str(high)
    connection = MySocket(sock)
    connection.send_msg(msg)
    result = connection.recv_msg().decode('utf-8') + " "
    sock.close()
    return result


def server(ports=None):
    if ports is None:
        ports = [31337]
    for port in ports:
        Thread(target=serv_proc, args=[port]).start()


def client(addresses, ports, low, up):
    connections = []
    sockets = []
    range = up - low
    toServRange = range // len(addresses)
    result = ""

    tm = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i, ip in enumerate(addresses):
            future = executor.submit(cli_thread, ip, int(ports[i]), low + i * toServRange, low + (i + 1) * toServRange)
            result += future.result()

    print(result)
    print("time: ", time.time() - tm)


def createParser():
    parser = argparse.ArgumentParser()
    groupCS = parser.add_mutually_exclusive_group()
    groupCS.add_argument('-s', '--server', action='store_true', help="Run as a server")
    groupCS.add_argument('-c', '--client', action='store_true', help="Run as a client")
    parser.add_argument('-a', '--address', help="SERVER address")
    parser.add_argument('-p', '--port', help="ports of the server")
    parser.add_argument('-l', type=int)
    parser.add_argument('-u', type=int)
    return parser


def main():
    parser = createParser()
    parameter = parser.parse_args(sys.argv[1:])
    # parser.print_help()
    if parameter.client:
        if parameter.address == None:
            parser.print_help()
            exit("Please, specify address")
        if parameter.l == None or parameter.u == None:
            parser.print_help()
            exit("Please, specify low and up")
        if parameter.l > parameter.u:
            exit("Low should be less or equals than up")
        servips = []
        for ip in parameter.address.split(","):
            servips.append(ip)
        ports = []
        for port in parameter.port.split(","):
            ports.append(port)
        client(servips, ports, parameter.l, parameter.u)
    if parameter.server:
        ports = []
        if parameter.port != None:
            for port in parameter.port.split(","):
                ports.append(int(port))

        else:
            ports = [31337]
        server(ports)


if __name__ == "__main__":
    main()
