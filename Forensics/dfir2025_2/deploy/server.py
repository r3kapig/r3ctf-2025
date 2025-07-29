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
                "What is the download link of the malware e.g: https://google.com",
                "https://gofile.io/d/snrbgl",
            )
            and self.ask_question(
                "What is the md5 value of the command executed by the first stage payload of the malware e.g: 12ccb49db8dd65c66ba3d4d52b25923a",
                "851ec4174b5490d53ba4ad06daf8a82a",
            )
            and self.ask_question(
                "3",
                "What is the function that executes the second stage malicious payload e.g: Function",
                "FinalizeUpdateConfig",
            )
            and self.ask_question(
                "4",
                "What is the MITRE ATT&CK ID of the technology used in the third stage e.g: T1000.000",
                "T1574.001",
            )
            and self.ask_question(
                "5",
                "What is the function that executes the third stage malicious payload e.g: Function",
                "GetInstallDetailsPayload",
            )
            and self.ask_question(
                "6",
                "What is the algorithm and key used to decrypt the third-stage malicious payload? e.g: des_ecb_1520a0462516f96e41b2da773e209042",
                "aes_cbc_89be5373aba9451d8d93e49ea23785b7",
            )
            and self.ask_question(
                "7",
                "What is the IP port of the malicious program to connect back to C2? e.g: 127.0.0.1:1337",
                "156.238.233.121:8080",
            )
            and self.ask_question(
                "8",
                "What is the algorithm and key used to decrypt the traffic? e.g: des_ecb_e3db6576de86854ab3e2bebf2338c5d7b36990103069b180330f4ef2aefd1b56",
                "aes_crt_b07c3644328c8ce428c408ceca9ea23038f2f248f87ceeb03e040aaab07c5638",
            )
            and self.ask_question(
                "9",
                "What is the name of the scheduled task created by the attacker? e.g: AutoShutdown",
                "SecurityUpdate",
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
