#!/usr/bin/python

import sys, socket

def main(args):
    ip = args[1]
    port = int(args[2])
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    file = 'sample.csv'

    fp = open(file, 'r')
    for line in fp:
        sock.sendto(line.encode('utf-8'), (ip, port))
    fp.close()

main(sys.argv)
