from base.server import Server
from base.socket_base import Socket
from socket import socket
from threading import Thread, Lock
import json
import logging
import time
from typing import Literal


class DummyCRDT(object):

        def __init__(self, gui) -> None:
            self.text = ""
            self.gui = gui

        def update(self, data: str):
            self.text = data
            print(self.text)
            # cur_pos = self.gui.get_cur_pos()

        def get_text(self) -> str:
            return self.text

        def update_from_gui(self, action: Literal["insert", "delete"], cur_pos, data: str):
            self.text = data


class Peer(object):
    
    def __init__(self, skt: Socket, id: int) -> None:
        self.skt = skt
        self.id = id


class Data(object):
        
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.headers: dict[str | bytes, str | bytes] = json.loads(data)


class ControlLayer(object):

    def __init__(self, url, gui=None, ishost=False, crdt=None) -> None:
        self.file_url = url
        self.gui = gui
        self.host_ip, self.host_port, self.host_file_path = self.get_host_addr(url)
        # self.host_ip = url.split("::")[0]
        # self.host_port = int(url.split("::")[1])
        # self.host_file_path = "::".join(url.split("::")[3:])
        if ishost:
            self.server = Server(self, IP=self.host_ip, port=self.host_port)
        else:
            self.server = Server(self)
        self.peerlist: list[Peer] = [Peer(self.server, 0)]
        self.conns: list[Socket] = []
        self.peerlist_lock = Lock()
        self.conns_lock = Lock()
        if crdt is None:
            crdt = DummyCRDT(gui)
        self.crdt = crdt
        self.ishost = ishost

        self.next_id = 1

        self.running = True

        # TODO: implement forwarding logic
        self.forward_matrix = []

    def get_host_addr(self, url: str):
        """
            returns the IP and port of the host from url
        """
        s = url.split("::")
        return s[0], int(s[1]), "::".join(s[3:])
    
    def get_peerlist(self):
        """
            returns a json encoded list of peers
        """
        peers = []
        for peer in self.conns:
            peers.append({
                "IP": peer.IP,
                "port": peer.port
            })
        return json.dumps(peers)
    
    def in_peerlist(self, IP: str, port: int) -> bool:
        """
            returns True if the peer is in the peerlist
        """
        for peer in self.conns:
            if peer.IP == IP and peer.port == port:
                return True
        return False

    def send_to_all(self, data: bytes):
        """
            sends `data` to all connections
        """
        failed = self.server.send_to_all(data, self.conns)
        print("failed", failed)

        # remove failed peers
        with self.conns_lock:
            self.conns = [self.conns[i] for i in range(len(self.conns)) if i not in failed]

    def add_headers(self, data: str, headers: dict[str, str]) -> bytes:
        headers["payload"] = data
        return json.dumps(headers).encode("utf-8")

    def format_peerlist(self, peerlist: str) -> bytes:
        return self.add_headers(peerlist, {"action": "peerlist"})

    def format_edit(self, data: str) -> bytes:
        return self.add_headers(data, {"action": "edit"})

    def format_conn(self, IP: str, port: int) -> bytes:
        return self.add_headers("", {"action": "conn", "IP": IP, "port": port})

    def action_conn(self, d: Data):
        IP, port = d.headers["IP"], d.headers["port"]

        conn = self.connect_to_host(IP, port)

        # send updated peerlist
        self.send_to_all(self.format_peerlist(self.get_peerlist()))

        # get_text() returns data to send to the new peer
        text = self.crdt.get_text()
        conn.send_data(self.format_edit(text))

    def action_edit(self, d: Data):
        self.crdt.update(d.headers["payload"])

    def connect_to_host(self, IP, port):
        conn = Socket(IP=IP, port=port)
        conn.connect()
        with self.conns_lock:
            self.conns.append(conn)
        return conn

    def action_peerlist(self, d: Data):
        """
        [
            {
                "IP": "<IP_ADDR>",
                "port": <NUM>
            },
            ...
        ]
        """
        peerlist = json.loads(d.headers["payload"])
        for peer in peerlist:
            IP, port = peer["IP"], peer["port"]
            if IP == self.server.IP and port == self.server.port:
                continue
            for p in self.conns:
                if p.IP == IP and p.port == port:
                    break
            else:
                self.connect_to_host(IP, port)

    def data_received(self, data: bytes, skt: Socket):
        """
            handles data received from a peer
        """
        d = Data(data)
        if d.headers["action"] == "peerlist":
            self.action_peerlist(d)

        elif d.headers["action"] == "conn":
            self.action_conn(d)

        elif d.headers["action"] == "edit":
            self.action_edit(d)

    def handle_client(self, conn: Socket, addr: tuple[str, int]):
        """
            handles a new client connection
        """
        conn = Socket(skt=conn)
        with self.peerlist_lock:
            self.peerlist.append(Peer(conn, self.next_id))
            self.next_id += 1

        try:
            while self.running:
                data = conn.recv_data()
                if data == b"":
                    break
                self.data_received(data, conn)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            logging.info(f"error: {e.strerror}")
        logging.info(f"Connection from {addr} closed")

    def send_dummy_data(self):
        while self.running:
            self.send_to_all(self.format_edit("abhinav"))
            time.sleep(1)

    def start(self):
        """
            starts the control layer
        """
        if not self.ishost:
            conn = self.connect_to_host(self.host_ip, self.host_port)
            conn.send_data(self.format_conn(self.server.IP, self.server.port))
        # Thread(target=self.send_dummy_data).start()
        self.server.start()

    def daemonize(self):
        """
            starts the control layer in a new thread
        """
        Thread(target=self.start).start()

    def stop(self):
        self.server.stop()
        for conn in self.conns:
            conn.socket.close()
        for peer in self.peerlist:
            peer.skt.socket.close()
        self.running = False
