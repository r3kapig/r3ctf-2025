from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, pair
from uuid import uuid4
import os
from random import randint

flag = os.environ["FLAG"]

class CHash:
    def __init__(self, ID):
        self.P = PairingGroup("SS512")
        self.msk = (self.P.random(ZR), self.P.random(ZR), self.P.random(ZR))
        g = self.P.random(G1)
        g_1 = g ** self.msk[0]
        g_2 = g ** self.msk[1]
        h_2 = g ** self.msk[2]
        u_2 = h_2 ** self.msk[0]
        self.pp = (g, g_1, g_2, h_2, u_2, pair(g, g), pair(g_2, g))
        print("This is your exclusive shopping mall, remember your membership number!", end=" ")
        print([self.P.serialize(x).decode() for x in self.pp])

        self.ID = self.P.hash(ID, ZR)
        t = self.P.random(ZR)
        self.td_ID = (t, g ** ((self.msk[1] - t) / (self.msk[0] - self.ID)))
    
    def _Hash(self, L, m, r):
        return self.pp[6] ** m * self.pp[5] ** r[0] * pair(r[1], self.pp[1] / (self.pp[0] ** self.ID)) * pair((self.pp[4] / (self.pp[3] ** self.ID)) ** L, r[2])
    
    def Hash(self, L, m):
        L = self.P.hash(L, ZR)
        m = self.P.hash(m, ZR)
        r = (self.P.random(ZR), self.P.random(G1), self.P.random(G1))
        h = self._Hash(L, m, r)
        return (h, r)

    def Check(self, L, m, h, r):
        L = self.P.hash(L, ZR)
        m = self.P.hash(m, ZR)
        return self._Hash(L, m, r) == h

    def Col(self, L, h, m, r, m_p):
        if not self.Check(L, m, h, r):
            print("Hash check failed")
            exit()
        L = self.P.hash(L, ZR)
        m = self.P.hash(m, ZR)
        m_p = self.P.hash(m_p, ZR)
        s, t_p = self.P.random(ZR), self.P.random(ZR)
        td_b_ID = (self.td_ID[0], self.td_ID[1] * (self.pp[4] / (self.pp[3] ** self.ID)) ** (L * t_p), (self.pp[1] / (self.pp[0] ** self.ID)) ** t_p)
        return (r[0] + (m - m_p) * td_b_ID[0], r[1] * (td_b_ID[1] * (self.pp[4] / (self.pp[3] ** self.ID)) ** (s * L)) ** (m - m_p), r[2] * (td_b_ID[2] * (self.pp[1] / (self.pp[0] ** self.ID)) ** s) ** (m_p - m))
    
class Chain:
    def __init__(self):
        self.Hash = CHash("ADMIN")
        self.Msg = []
        self.HashPointer = [self.Hash.msk[2]]
        self.Randomness = []
        self.Label = []
    
    def Add(self, msg):
        self.Label.append(uuid4().hex)
        h, r = self.Hash.Hash(self.Label[-1], self.Hash.P.serialize(self.HashPointer[-1]).decode() + msg)
        self.Msg.append(msg)
        self.HashPointer.append(h)
        self.Randomness.append(r)
    
    def ReWrite(self, msg, idx):
        self.Randomness[idx] = self.Hash.Col(self.Label[idx], self.HashPointer[idx + 1], self.Hash.P.serialize(self.HashPointer[idx]).decode() + self.Msg[idx], self.Randomness[idx], self.Hash.P.serialize(self.HashPointer[idx]).decode() + msg)
        self.Msg[idx] = msg

    def Check(self):
        for i in range(len(self.Msg)):
            if not self.Hash.Check(self.Label[i], self.Hash.P.serialize(self.HashPointer[i]).decode() + self.Msg[i], self.HashPointer[i + 1], self.Randomness[i]):
                print("Chain check failed")
                exit()
    
    def Show(self):
        for i in range(len(self.Msg)):
            print("HP:", self.Hash.P.serialize(self.HashPointer[i]).decode())
            print("R:", (self.Hash.P.serialize(self.Randomness[i][0]).decode(), self.Hash.P.serialize(self.Randomness[i][1]).decode(), self.Hash.P.serialize(self.Randomness[i][2]).decode()))
            print("L:", self.Label[i])
            print("M:", self.Msg[i])
        print("END")

class Task:
    def __init__(self):
        self.chain = Chain()
        self.chain.Add("Selling|gift|100")
    
    def Work(self):
        money = randint(1, 10)
        self.chain.Add("Work|" + str(money))
    
    def Buy(self):
        self.chain.Add("Buy")
        self.chain.Add("Selling|gift|100")
    
    def RefundOldest(self):
        money = randint(1, 10)
        for idx in range(len(self.chain.Msg)):
            if self.chain.Msg[idx] == "Buy":
                self.chain.ReWrite("Work|" + str(money), idx)
                break

    def Show(self): return self.chain.Show()

    def ReWrite(self, idx, msg, r):
        r = r[1:-1].split(", ")
        r[0] = self.chain.Hash.P.deserialize(r[0][1:-1].encode())
        r[1] = self.chain.Hash.P.deserialize(r[1][1:-1].encode())
        r[2] = self.chain.Hash.P.deserialize(r[2][1:-1].encode())
        self.chain.Msg[idx] = msg
        self.chain.Randomness[idx] = r

    def RunPayment(self):
        self.chain.Check()
        money = 0
        resp = ""
        shop = []
        for i in range(len(self.chain.Msg)):
            data = self.chain.Msg[i].split("|")
            if data[0] == "Selling": 
                shop.append((data[1], int(data[2])))
                resp += "now selling " + data[1] + ", $" + data[2] + "\n"
            elif data[0] == "Work": 
                money += int(data[1])
                resp += "earn $" + data[1] + ", total $" + str(money) + "\n"
            elif data[0] == "Buy": 
                if len(shop) == 0: resp += "No goods for U\n"
                else:
                    if money < shop[0][1]: resp += "Not enough money\n"
                    else:
                        money -= shop[0][1]
                        goods = shop[0][0]
                        shop.pop(0)
                        if goods == "flag": goods = flag
                        resp += "Buy " + goods + ", remain $" + str(money) + "\n"
        return resp
    
BANNER = br"""
                                                      01
                                                      0001           0
                                                      0000       11000
                                                      0001 1  11  0000
                                                      0000 10000   000
                                                      00001100001  000
                                                      0000000000000000
                                                      0111100000000000
                                                            0000   100
               1101                                         0000     1
            1000000001       01                             0000
           00000000000000000000                             0000
          000000000000000000000100000111                    1111
         1000000000000000000000000000000000001              1  1
          1000000000000000000011        111000001           0111
             000000000000000                  10001         1010
            100000000000001                      1001       1  1
            100000001111                           001      1110     1
             100000   11                       100  101     11 1   111
               000  10001     1001111110001    1001  10     000001  0
              1000   101    001           100         0011110000  1011
           1  1001         01   11     1    00      010111  0000   10
        0     1001        10    00    000   10     11 0 1 0 0000 101
       0 01  1100011       00               00      0 01    0000
         0  010 000  1111   101           101        0  11110000
         11 1    000       001 10000100001          0       0000
           1001 0 1000 001                        01        0000
               10 00000001                     100          0000
                      1000011              10001            0000
                          100000000000000001                0000
                                                            0000
"""

def Welcome():
    print(BANNER.decode())
    print('''Welcome to R3Coin! U can buy any gift U want, but U need to work to earn money.''')

def menu():
    print('''1. Work, work
2. Buy gift
3. Refund oldest gift
4. Show my bill
5. Write my bill
6. Run payment
> ''', end="")
    return int(input())

def main():
    Welcome()
    prob = Task()
    while 1:
        choice = menu()
        if choice == 1: prob.Work()
        elif choice == 2: prob.Buy()
        elif choice == 3: prob.RefundOldest()
        elif choice == 4: prob.Show()
        elif choice == 5: prob.ReWrite(int(input("Index> ")), input("Message> "), input("Randomness> "))
        elif choice == 6: break
        else: print("Invalid choice")
    print(prob.RunPayment())

main()