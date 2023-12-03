from socket import socket, SOCK_STREAM, AF_INET, SOCK_DGRAM
from typing import Tuple


class Socket(object):
    """
        An extension on socket.io to atomize sending and receiving all data
        TODO: Encrypt all communication
    """

    def __init__(self, IP=None, port=None, skt: socket = None,
                 header=12, format="utf-8") -> None:
        """
            If `skt` is None a new socket object is created
        """
        if skt is not None:
            self.socket = skt
            if IP is None or port is None:
                self.IP, self.port = self.socket.getsockname()
        else:
            self.socket = self.new_socket()
        if IP is not None and port is not None:
            self.IP = IP
            self.port = port
        self.HEADER = header
        self.FORMAT = format
        self.addr = (IP, port)
        self.running = False

    def get_ip(self) -> str:
        """
            returns the IP address of the socket
        """
        conn = socket(AF_INET, SOCK_DGRAM)
        conn.connect(("10.255.255.255", 1))
        return conn.getsockname()[0]

    def new_socket(self) -> socket:
        """
            creates a new socket object
        """
        return socket(AF_INET, SOCK_STREAM)

    def connect(self, addr: Tuple[str, int] = None, conn: socket = None):
        """
            connects to the server
        """
        if conn is None:
            conn = self.socket
        if addr is None:
            addr = self.addr
        conn.connect(self.addr)

    def send_to_all(self, data: bytes|str, conns = []):
        """
            sends `data` to all connections in `conns` or `self.connections`
        """
        conn: Socket
        failed = []
        conns = conns.copy()
        for i, conn in enumerate(conns):
            try:
                self.send_data(data, conn.socket)
            except Exception as e:
                failed.append(i)
        return failed

    def send_data(self, data: bytes|str, conn: socket = None):
        """
            sends all data over `conn` or `self.socket`.
            Blocks untill all data is sent or an error in encountered
        """

        if isinstance(data, str):
            data = data.encode(self.FORMAT)

        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes or str, got {type(data)}")

        if conn is None:
            conn = self.socket
        ln = str(len(data)).encode(self.FORMAT)

        # send length of data
        conn.sendall(ln + ' '.encode(self.FORMAT)*(self.HEADER-len(ln)))
        conn.sendall(data)  # send data

    def recv_data(self, conn: socket = None) -> bytes:
        """
            receives all data from `conn` or `self.socket`.
            Blocks untill all data is sent or an error in encountered
        """
        if conn is None:
            conn = self.socket
        ln = data = b''
        t = self.HEADER

        # first get length of data
        while t:
            temp = conn.recv(t)
            if not temp:
                return b''
            ln += temp
            t -= len(temp)
        ln = int(ln)

        # then get data
        while ln:
            temp = conn.recv(ln)
            if not temp:
                return b''
            ln -= len(temp)
            data += temp

        return data
