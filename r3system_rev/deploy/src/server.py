from user import * 
from secret import secret_flag_part
import os, signal, inspect, utils, server, user

FLAG = os.environ.get('FLAG', 'r3ctf{dummy_flag}')

def _handle_timeout(signum, frame):
    raise TimeoutError('function timeout')

timeout = 480
signal.signal(signal.SIGALRM, _handle_timeout)
signal.alarm(timeout)

print("Welcome to R3System Revenge!")
print("Sorry for the inconvenience, we have fixed the bugs in the previous version.")
print("Now you should give me the secret flag part from `r3system`")
part_of_secret_flag = input("Please input the secret flag part: ")

if part_of_secret_flag == secret_flag_part:
    print("Correct! You can now access the system.")
else:
    print("Incorrect flag part. Access denied.")
    exit()

if input("Do you want to see the source code? [y/n]: ").lower() == 'y': 
    print("[+] Here is the utils.py code:")
    print("="*50+"\n"+inspect.getsource(utils)+"\n"+"="*50+"\n") 
    print("[+] Here is the user.py code:")
    print("="*50+"\n"+inspect.getsource(user)+"\n"+"="*50+"\n") 
    print("[+] Here is the server.py code:")
    print("="*50+"\n"+inspect.getsource(server)+"\n"+"="*50+"\n")

LOGIN_MENU = """[+] Nice day!
[1]. Log In [Password]
[2]. Log In [Token]
[3]. Sign Up
[4]. Guess Flag Token
[5]. Exit
"""

SYSTEM_MENU = """ 
[1]. Reset Password
[2]. Exchange keys with sb.
[3]. Get news on public channels
[4]. Get your private key & public key
[5]. Quit
"""

FLAG_TOKEN, PoW_KinG = os.urandom(32), False

PublicChannels,login_tag,USER = b"",False,Users()

AliceUsername,BobUsername = b'AliceIsSomeBody',b'BobCanBeAnyBody'

USER.register(AliceUsername,os.urandom(166)) 
USER.register(BobUsername,os.urandom(166))

def LoginSystem(USER): 
    global login_tag, FLAG_TOKEN, PoW_KinG
    option = int(input("Now input your option: "))
    if option == 1:
        username = bytes.fromhex(input("Username[HEX]: "))
        password = bytes.fromhex(input("Password[HEX]: "))
        login_tag,msg = USER.login_by_password(username,password)
        print(msg.decode())
        if login_tag: return username 

    elif option == 2:
        username = bytes.fromhex(input("Username[HEX]: "))
        if username == AliceUsername or username == BobUsername:
            print("You can't login with token!")
            return
        token = bytes.fromhex(input("Token[HEX]: "))
        login_tag,msg = USER.login_by_token(username,token)
        print(msg.decode())
        if login_tag: return username 

    elif option == 3:
        username = bytes.fromhex(input("Username[HEX]: "))
        if username == AliceUsername or username == BobUsername:
            print("You can't register with this username!")
            return
        password = bytes.fromhex(input("Password[HEX]: "))
        register_tag,msg = USER.register(username,password) 
        if register_tag: print(f"Register successfully, {username} 's token is {msg.hex()}.")
        else: print(msg.decode())

    elif option == 4:
        guess_flag_token = bytes.fromhex(input("Flag Token[HEX]: "))
        if guess_flag_token == FLAG_TOKEN:
            print(f"Congratulations! You guessed the flag token correctly! The flag is: {FLAG}")
            exit()

    else: exit()

def R3System(USERNAME): 
    global login_tag,PublicChannels
    option = int(input(f"Hello {USERNAME.decode()}, do you need any services? "))

    if option == 1: 
        new_password = bytes.fromhex(input(f"New Password[HEX]: "))
        tag,msg = USER.reset_password(USERNAME,new_password)
        print(msg.decode())

    elif option == 2:
        ToUsername = bytes.fromhex(input(f"ToUsername[HEX]: "))
        if ToUsername not in USER.usernames: print("ERROR");return False
        PublicChannels += transfer_A2B(USER,USERNAME,ToUsername,b" My Pubclic key is: " + USER.getsb_public_key(USERNAME).hex().encode()) + \
            transfer_A2B(USER,ToUsername,USERNAME,b" My Pubclic key is: " + USER.getsb_public_key(ToUsername).hex().encode())
        ToPublickey = b2p(USER.getsb_public_key(ToUsername))
        change_key = USER.ecdhs[USERNAME].exchange_key(ToPublickey)
        print((f"Exchanged Key is: {change_key.hex()}"))
    elif option == 3: print(PublicChannels.decode())
    elif option == 4: print(f"Your private key is: {USER.view_private_key(USERNAME).hex()}\nYour public key is: {USER.getsb_public_key(USERNAME).hex()}")
    elif option == 5: login_tag = False

def Alice_transfer_flag_to_Bob(AliceUsername,BobUsername):
    global PublicChannels, FLAG_TOKEN
    PublicChannels += transfer_A2B(USER,AliceUsername,BobUsername,b" Halo bob, I will give your my flag after we exchange keys.") + \
        transfer_A2B(USER,BobUsername,AliceUsername, b" OK, I'm ready.") + \
        transfer_A2B(USER,AliceUsername,BobUsername, b" My Pubclic key is: " + USER.getsb_public_key(AliceUsername).hex().encode()) + \
        transfer_A2B(USER,BobUsername,AliceUsername, b" My Pubclic key is: " + USER.getsb_public_key(BobUsername).hex().encode()) + \
        transfer_A2B(USER,AliceUsername,BobUsername, b" Now its my encrypted flag:") + \
        transfer_A2B(USER,AliceUsername,BobUsername, FLAG_TOKEN , enc=True) + \
        transfer_A2B(USER,BobUsername,AliceUsername, b" Wow! I know your flag now! ")

Alice_transfer_flag_to_Bob(AliceUsername,BobUsername)

while 1: 
    if not login_tag: print(LOGIN_MENU); USERNAME = LoginSystem(USER) 
    else: print(SYSTEM_MENU); R3System(USERNAME)