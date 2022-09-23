import struct
flag = 0
ack = 1
syn = 0
fin = 0
if ack: 
    flag = flag | 4
if syn:
    flag = flag | 2
if syn:
    flag = flag | 1
flag = 4
seq = 5
ack = 7

payload = 'adasd'
a = struct.pack('3i', flag, seq, ack)
print(a[:8], len(a))
print(len(bytes(seq)))
b = struct.unpack('3i', a[:12])
print(b)
c = bytes('aasdvsd', encoding = 'utf-8')
print(str(c, encoding = 'utf-8'))
l = []
i = 0
while i + 5 < len(c):
    l.append(c[i:i+5])
    i = i + 5
l.append(c[i:-1])
print(l)
w = 10 / 6
print(int(w), w)
ACK = 0
for ACK in range(4):
    print(ACK)
    ACK = ACK + 1
try:
    x = 5
    if x < 7:
        raise Exception("x < 7")
    print('success')
    asdasdasda
except Exception:
    print('in exception')
l = [0, 1, 2, 3]
while len(l):
    del l[:1]
    print(l)
a = 0
for i in range(1, 21):
    a += 1
    print("%4d" % i, end=" ")
print(type('a'))
char = bytes('a', encoding = 'utf-8')
assert(0)
print(char)