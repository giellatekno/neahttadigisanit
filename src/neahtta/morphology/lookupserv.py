#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
A lookup server that uses threads to handle multiple clients at a time.
Called from the ped-interface (forms.py)
"""

import os
import re
import select
import socket
import sys
import threading
import time
from threading import Lock

import pexpect


class Server:
    def __init__(self, cmd, name, port=9000):
        self.host = ''
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []
        self.lookup = cmd

        logfile = "proc.%s.log" % name
        f = open(logfile, 'a')

        self.look = pexpect.spawn(self.lookup)
        self.look.logfile = f
        self.lock = threading.Lock()

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
                print "Could not open socket: " + message
                sys.exit(1)

    def run(self):
        self.open_socket()
        input = [self.server, sys.stdin]
        running = 1
        while running:
            inputready, outputready, exceptready = select.select(input, [], [])

            for s in inputready:
                if s == self.server:
                    # handle the server socket
                    c = Client(self.server.accept(), self.look, self.lock)
                    c.start()
                    self.threads.append(c)
            time.sleep(1)

        self.server.close()
        for c in self.threads:
            c.join()


class Client(threading.Thread):
    def __init__(self, (client, address), look, lock):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024
        self.look = look
        self.lock = lock
        # self.lookup2cg = " | /Users/pyry/gtsvn/gt/script/lookup2cg"

    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            data = data.strip()
            if not data:
                self.client.close()
                running = 0
                continue

            data2 = data
            # clean the data for command line
            c = [
                ";", "<", ">", "*", "|", "`", "&", "$", "!", "#", "(", ")",
                "[", "]", "{", "}", ":", "@", "\"", "\r"
            ]
            for a in c:
                data = data.replace(a, '')

            # Take out non-breaking space. Try to avoid errors.
            try:
                data2 = data.decode('utf-8')
                data2 = data2.replace(unichr(160), "")
                data = data2.encode('utf8')
            except:
                #data = data.encode('utf-8')
                #f.write("Not utf-8: " + data)
                self.client.send("error")
                continue

                #data = re.sub(r'[^\wáŋčžšđŧÁŊĐÁŠŦŽČ_- åäöÅÄÖæøÆØ]+', '',data, re.U)

            # if the data contained only special characters, return the original data.
            if not data:
                self.client.send("error")
                continue

            # quit with q
            if (data.strip() == 'q' or data == 'Q'):
                self.client.close()
                running = 0
                continue

            data = data.strip() + "\n"

            #f = open('/var/log/lserv.log', 'a')

            self.lock.acquire()
            #f.write("input: "+ data)
            #f.write("\n")
            self.look.sendline(data)
            index = self.look.expect(
                ['\r?\n\r?\n', 'ERROR', pexpect.EOF, pexpect.TIMEOUT])

            #If there is an error, then restart the lookup process
            if index == 1 or index == 2 or index == 3:
                try:
                    self.look.read_nonblocking(timeout=1)
                except:
                    self.client.send("error")
                self.client.send("error")
                self.lock.release()
                continue

            if index == 0:
                self.lock.release()
                result = self.look.before

                # hack for removing the stderr from lookup 0%>>>>>>100% ...
                result = result.replace('100%', '')
                result = result.replace('0%', '')

                lstring = ""
                for r in result.splitlines():
                    res = r.rstrip('>').lstrip('>')
                    if res.rstrip().lstrip():
                        lstring = lstring + res + "\n"

                # cg_call = "echo \"" + lstring + "\"" + self.lookup2cg
                #print "jee", cg_call
                self.client.send(result)

                # try:
                #     anl = os.popen(cg_call).readlines()
                #
                #     analyzed = ""
                #     for a in anl:
                #         analyzed = analyzed + a
                #
                #     self.client.send(analyzed)
                # except:
                #     self.client.send(cg_call)
                #     self.client.send("error")


if __name__ == "__main__":
    s = Server(
        cmd="lookup -flags mbTT /Users/pyry/gtsvn/gt/sme/bin/sme.fst",
        name="smelookup",
        port=9001)
    s.run()
