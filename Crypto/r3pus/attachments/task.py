from Crypto.Util.number import getPrime
from random import randint
import signal

def _handle_timeout(signum, frame):
    raise TimeoutError('function timeout')

timeout = 60
signal.signal(signal.SIGALRM, _handle_timeout)
signal.alarm(timeout)



print("Welcome to ottoL repus.")

bitsize = 1024
flag = open("flag",'r').read()
p,q = getPrime(bitsize // 2),getPrime(bitsize // 2)
score = 0
chances = 0

for _ in range(16):
    print("1. Game Start.")
    print("2. Check score.")
    print("Score:", score)
    coi = int(input())
    
    if coi == 1:
        secret = randint(0, 2 ** 64)
        r1,r2 = randint(0, q), randint(0,p)
        u = randint(0, 2 ** (bitsize // 2))
        v = (secret * 2 ** 128 + randint(0, 2 ** 128)) - u
        x = u + r1 * p
        y = v + r2 * q
        print("x =", x)
        print("y =", y)
        guess = int(input("Give me the secret number: "))
        if guess == secret:
            score += 1
            print("You are smart!")
        else:
            print("~")
    elif coi == 2:
        print("Your scores:", score)
        if score >= 10:
            print(flag)
        else:
            print("Fighting!")
    elif coi == p:
        print("Wtf? You known the real secret number!")
        print(flag)
