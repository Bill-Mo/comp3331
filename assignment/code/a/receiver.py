# the version of this program is python3

from socket import *
from packet import packet, unpack

import sys
import time

def receiver(receiver_port, fileReceived):

    # https://github.com/arturenault/reliable-transport-protocol/blob/master/Receiver.py
    server_socket = socket(AF_INET, SOCK_DGRAM) 
    server_socket.bind(('localhost', receiver_port))
    socket.settimeout(server_socket, 10)

    # create a log txt
    log_txt = open('Receiver_log.txt', 'a+')

    # Received a packet
    packet_received, addr = server_socket.recvfrom(2048)
    ip, port = addr
    syn = unpack(packet_received)

    assert(syn.s and syn.seq == 0)
    pass_time = time.time()

    # record rcv to the log
    generate_write(log_txt, pass_time, "rcv", 'S', syn.seq, syn.data, syn.ACK)
    
    # syn
    ACK = syn.seq + 1
    ack_syn = packet(port, 0, ACK, 1, 1, 0, bytes('', encoding = 'ascii'))
    server_socket.sendto(ack_syn.byte_packet, addr)
    # Send an ACK packet

    # record snd to the log
    generate_write(log_txt, pass_time, "snd", 'SA', syn.seq, syn.data, syn.ACK)
    packet_received, addr = server_socket.recvfrom(2048)
    syn_ack = unpack(packet_received)

    # record rcv to the log
    generate_write(log_txt, pass_time, "rcv", 'A', syn_ack.seq, syn_ack.data, syn_ack.ACK)


    ACK = 1
    seq = 0
    while True:
        packet_received, addr = server_socket.recvfrom(2048)
        sent_packet = unpack(packet_received)
        
        if sent_packet.f:
            break

        # record rcv to the log
        generate_write(log_txt, pass_time, "rcv", 'D', sent_packet.seq, sent_packet.data, sent_packet.ACK)

        if sent_packet.seq == ACK: 
            ACK = sent_packet.seq + len(sent_packet.data)
            seq = sent_packet.ACK
            message = str(sent_packet.data, encoding = 'ascii')
            
            f = open(fileReceived, 'a+')
            f.write(message)
            f.close()

        ack_packet = packet(port, seq, ACK, 1, 0, 0, bytes('', encoding = 'ascii'))
        server_socket.sendto(ack_packet.byte_packet, addr)

        # record snd to the log
        generate_write(log_txt, pass_time, "snd", 'A', ack_packet.seq, ack_packet.data, ack_packet.ACK)

    # receive a fin packet
    generate_write(log_txt, pass_time, "rcv", 'F', sent_packet.seq, sent_packet.data, sent_packet.ACK)
    
    # send a fin ack
    fin_ack = packet(port, sent_packet.ACK, sent_packet.seq + 1, 1, 0, 0, bytes('', encoding = 'ascii'))
    server_socket.sendto(fin_ack.byte_packet, addr)
    generate_write(log_txt, pass_time, "snd", 'A', fin_ack.seq, fin_ack.data, fin_ack.ACK)
    
    # send a fin packet
    fin = packet(port, fin_ack.seq, fin_ack.ACK, 0, 0, 1, bytes('', encoding = 'ascii'))
    server_socket.sendto(fin.byte_packet, addr)
    generate_write(log_txt, pass_time, "snd", 'F', fin.seq, fin.data, fin.ACK)

    # receive a packet
    packet_received, addr = server_socket.recvfrom(2048)
    fin_ack = unpack(packet_received)
    generate_write(log_txt, pass_time, "rcv", 'A', fin_ack.seq, fin_ack.data, fin_ack.ACK)
    
    # succeed
    if fin_ack.ACK == fin.seq + 1:
        server_socket.close()


    log_txt.close()


def generate_write(log_txt, pass_time, state, type_of_packet, seq_number, contents, ack_number):
    
    current_time = time.time()
    interval = '{:.2f}'.format((current_time - pass_time) * 1000)
    number_of_bytes = len(contents)
    
    log = state + '\t\t' + interval + '\t\t' + type_of_packet + '\t\t' + str(seq_number) + \
          '\t\t' + str(number_of_bytes) + '\t\t' + str(ack_number) + '\n'
    log_txt.write(log)


if __name__ == '__main__':

    receiver_port = int(sys.argv[1])   
    # (use a value greater than 1023 and less than 65536)
    # the port number on which the Receiver will open a UDP socket for receiving datagrams from the Sender.
    fileReceived = sys.argv[2]
    # (to be created by your program into which received data is written)
    # the name of the text file into which the text sent by the sender should be stored 
    # (this is the file that is being transferred from sender to receiver).

    receiver(receiver_port, fileReceived)