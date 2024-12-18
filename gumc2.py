#!/usr/bin/env python3

"""

gumc, Grande Unified Multicast Client


"""
import argparse
import io
import select
import socket
import struct
import sys
import time

MILLION = 1024 << 10
DGRAM_SIZE = 1316
INSTUFF = "udp://@235.35.3.5:3535"
OUTSTUFF = sys.stdout.buffer
TIMEOUT = 60


class GumC:
    """

    GumC, Grande Unified Multicast Client

    """

    def __init__(self, args):
        self.addr, self.port = self._addr_port(args.instuff)
        self.outstuff = args.outstuff
        if self.outstuff != OUTSTUFF:
            self.outstuff = open(self.outstuff, "wb")
        self.total_bytes = 0
        self.start_time = time.time()

    def _addr_port(self, uri):
        if "udp://@" in uri:
            addr, port = (uri.split("udp://@")[1]).rsplit(":", 1)
        else:
            addr, port = (uri.split("udp://")[1]).rsplit(":", 1)
        port = int(port)
        return addr, port

    def elapsed(self):
        """
        elapsed calculates how long the client has been reading packets.
        """
        return time.time() - self.start_time

    def do(self):
        active = io.BytesIO()
        self.start_time = time.time()
        interface_ip = "0.0.0.0"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 32)
        )
        sock.bind(("", self.port))
        sock.setsockopt(
            socket.SOL_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton(self.addr) + socket.inet_aton(interface_ip),
        )
        with self.outstuff as a_file:
            while True:
                received = sock.recv(DGRAM_SIZE)
                self.total_bytes += DGRAM_SIZE
                active.write(received)
                self.show_rate()
                if not (self.total_bytes % 10):
                    a_file.write(active.getbuffer())
                    active = io.BytesIO()
            a_file.write(active.getbuffer())

    def show_rate(self):
        """
        show_rate shows read rate of gumc.
        """
        elapsed = self.elapsed()
        rate = (self.total_bytes / MILLION) / elapsed
        one = f"\t{self.total_bytes/MILLION:0.2f} MB received in "
        two = f"{elapsed:5.2f} seconds. {rate:3.2f} MB/Sec"
        print(one, two, end="\r", file=sys.stderr)


def argue():
    """
    parse_args parse command line args
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--instuff",
        default=INSTUFF,
        help="Input, default is 'udp://@235.35.3.5:3535' ",
    )

    parser.add_argument(
        "-o",
        "--outstuff",
        default=OUTSTUFF,
        help="Output, default is sys.stdout.buffer(for piping)",
    )

    return parser.parse_args()


def cli():
    """
    cli  makes a fully functional command line tool

    usage: gumc [-h] [-i INSTUFF]  [-o OUTSTUFF]

    optional arguments:
      -h, --help            show this help message and exit
      -i INSTUFF, --instuff INSTUFF
                            Input, default is 'udp://@235.35.3.5:3535'
      -o OUTSTUFF, --outstuff OUTSTUFF
                            Output, default is sys.stdout.buffer(for piping)

    """
    args = argue()
    gumc = GumC(args)
    gumc.do()


if __name__ == "__main__":
    cli()
