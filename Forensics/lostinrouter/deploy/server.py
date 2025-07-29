import hashlib
import json
import random
import socketserver
import string
from os import environ

table = string.ascii_letters + string.digits

banner = r"""
             __        __   _                            _____     
             \ \      / /__| | ___ ___  _ __ ___   ___  |_   _|__                           
              \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \   | |/ _ \                          
               \ V  V /  __/ | (_| (_) | | | | | |  __/   | | (_) |                         
                \_/\_/ \___|_|\___\___/|_| |_| |_|\___|   |_|\___/                          
                                                                                            
             ____  _____  ____ _____ _____   ____   ___ ____  ____                          
            |  _ \|___ / / ___|_   _|  ___| |___ \ / _ \___ \| ___|                         
            | |_) | |_ \| |     | | | |_      __) | | | |__) |___ \                         
            |  _ < ___) | |___  | | |  _|    / __/| |_| / __/ ___) |                        
            |_| \_\____/ \____| |_| |_|     |_____|\___/_____|____/  
"""


def sanitize(inp):
    inp = str(inp).strip()
    inp = inp.replace(" ", "")
    return inp


class Task(socketserver.BaseRequestHandler):
    scoreboard = []
    answers = {}

    def ask_question(self, number, question, format):
        self.send(f"Q{number}) {question}".encode())
        self.send(f"Example: {format}\n".encode())
        answer = sanitize(self.recv(prompt=b"Answer: ").strip().decode())
        print(f"Answer for Q{number}: {answer} ?= {self.answers[number]}")
        if (
            hashlib.md5(answer.encode()).hexdigest()
            == hashlib.md5(self.answers[number].encode()).hexdigest()
        ):
            self.send(b"Correct!\n")
            return True
        else:
            self.send(b"Wrong answer!\nExiting...")
            self.request.close()
            return False

    def _recvall(self):
        BUFF_SIZE = 2048
        data = b""
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break
        return data.strip()

    def send(self, msg, newline=True):
        try:
            if newline:
                msg += b"\n"
            self.request.sendall(msg)
        except Exception as e:
            print("Error sending message:", msg, e)
            pass

    def recv(self, prompt=b""):
        self.send(prompt, newline=False)
        return self._recvall()

    def proof_of_work(self):
        proof = ("".join([random.choice(table) for _ in range(20)])).encode()
        sha = hashlib.sha256(proof).hexdigest().encode()
        self.send(b"[+] sha256(XXXX+" + proof[4:] + b") == " + sha)
        XXXX = self.recv(prompt=b"[+] Plz Tell Me XXXX :")
        if (
            len(XXXX) != 4
            or hashlib.sha256(XXXX + proof[4:]).hexdigest().encode() != sha
        ):
            return False
        return sha.decode()

    def ask_questions(self):
        ok = (
            self.ask_question(
                "1",
                "What is the OS version of the router?  ",
                "24.10.2",
            )
            and self.ask_question(
                "2",
                "What is the IP address of the attacker's machine?",
                "114.51.41.91",
            )
            and self.ask_question(
                "3",
                "What is the CVE number of the vulnerability exploited by the attacker?",
                "CVE‑2025‑32463",
            )
            and self.ask_question(
                "4",
                "What program's configuration was modify by the attacker to do persistence?",
                "rsyncd",
            )
            and self.ask_question(
                "5",
                "What is the host hijacked by the attacker?",
                "dashboard.company.com",
            )
            and self.ask_question(
                "6",
                "What host did the attacker use to host malicious artifacts? ",
                "foo-bar-deadbe.varcel.app",
            )
        )
        return ok

    def handle(self):
        with open("answers.json", "r") as f:
            # Load answers from a JSON file
            print("Loading answers from answers.json")
            self.answers = json.load(f)
        self.send(banner.encode())
        hash = self.proof_of_work()
        print(f"Proof of work hash: {hash}")
        if not hash:
            self.request.close()
            return
        if not self.ask_questions():
            return
        # check answers
        self.send(b"Congratulations! You have completed the task.")
        # flag in environment variable FLAG
        flag = environ.get("FLAG", "R3CTF{just_for_testing}")
        self.send(f"Flag: {flag}".encode())


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 10002
    print("HOST:POST " + HOST + ":" + str(PORT))
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
