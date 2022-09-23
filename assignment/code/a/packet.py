import struct

class packet:
    def __init__(self, dest_port, seq, ACK, ack, syn, fin, data):
        self.dest_port = dest_port
        self.seq = seq
        self.ACK = ACK
        self.flag = 0
        self.a = ack
        self.s = syn
        self.f = fin
        self.header = (self.dest_port, self.seq, self.ACK, self.a, self.s, self.f)
        self.data = data 
        self.byte_packet = struct.pack('6i', self.dest_port, self.seq, self.ACK, self.a, self.s, self.f) + self.data
    


# Break a packet into its component parts
def unpack(packet_received):

    # https://grzegorzgutowski.staff.tcs.uj.edu.pl/SK/05-cwiczenia/server.py
    header = struct.unpack('6i', packet_received[:24])
    dest_port, seq, ACK, a, s, f = header
    data = packet_received[24:]
    return packet(dest_port, seq, ACK, a, s, f, data)