from socket import *
from packet import packet, unpack
from receiver import generate_write

import time
import sys
import random
import math



pass_time = time.time()
def sender(receiver_host_ip, receiver_port, fileToSend, MWS, MSS, timeout, pdrop, seed):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    socket.settimeout(client_socket, timeout / 1000)
    print('The sender is ready to send')

    # Make a log file
    log_txt = open('Sender_log.txt', 'a+')

    # Connection setup
    
    syn = packet(receiver_port, 0, 0, 0, 1, 0, bytes('', encoding = 'ascii'))
    address = (receiver_host_ip, receiver_port)
    client_socket.sendto(syn.byte_packet, address)

    # sent a syn packet
    generate_write(log_txt, pass_time, "snd", 'S', syn.seq, syn.data, syn.ACK)

    packet_received, address = client_socket.recvfrom(2048)
    ack_syn = unpack(packet_received)

    # received a packet
    generate_write(log_txt, pass_time, "rcv", 'SA', ack_syn.seq, ack_syn.data, ack_syn.ACK)

    assert(ack_syn.ACK == 1)
    print('Received packet is an ACK to syn')
    ack_ack_syn = packet(receiver_port, ack_syn.ACK, ack_syn.seq + 1, 1, 0, 0, bytes('', encoding = 'ascii'))
    client_socket.sendto(ack_ack_syn.byte_packet, address)
    generate_write(log_txt, pass_time, "snd", 'A', ack_ack_syn.seq, ack_ack_syn.data, ack_ack_syn.ACK)

    # Read message

    f = open(fileToSend)
    data_to_send = f.read()
    f.close()
    byte_message = bytes(data_to_send, encoding='ascii')
    # Break message to MSS bytes of payloads
    data = []
    i = 0
    while i + MSS < len(byte_message):
        data.append(byte_message[i:i + MSS])
        i = i + MSS
    data.append(byte_message[i:len(byte_message)])

    # Send message
    window_size = int(MWS/MSS)
    seq = 1
    ACK = 1
    last_received_ACK = 1
    while len(data):
        seq, ACK, last_received_ACK = pass_packet(data, window_size, seq, ACK, pdrop, address, client_socket, log_txt, last_received_ACK, MSS)

    # Teardown

    send_fin = packet(receiver_port, last_received_ACK, ACK, 0, 0, 1, bytes('', encoding = 'ascii'))
    client_socket.sendto(send_fin.byte_packet, address)

    # sent a fin packet
    generate_write(log_txt, pass_time, "snd", 'F', send_fin.seq, send_fin.data, send_fin.ACK)

    packet_received, address = client_socket.recvfrom(2048)
    ack_fin = unpack(packet_received)

    # received a packet
    generate_write(log_txt, pass_time, "rcv", 'A', ack_fin.seq, ack_fin.data, ack_fin.ACK)

    assert(ack_fin.ACK - last_received_ACK == 1)
    packet_received, address = client_socket.recvfrom(2048)
    received_fin = unpack(packet_received)

    # received a packet
    generate_write(log_txt, pass_time, "rcv", 'FA', received_fin.seq, received_fin.data, received_fin.ACK)

    assert(received_fin.f == 1)
    ack_received_fin = packet(receiver_port, last_received_ACK, received_fin.seq + 1, 1, 0, 0, bytes('', encoding = 'ascii'))
    client_socket.sendto(ack_received_fin.byte_packet, address)          
    # send a fin ack packet
    generate_write(log_txt, pass_time, "snd", 'A', ack_received_fin.seq, ack_received_fin.data, ack_received_fin.ACK)    
    client_socket.close()
            
    log_txt.close()

def pass_packet(data, window_size, seq, ACK, pdrop, address, client_socket, log_txt, last_received_ACK, MSS):
    count = 0
    window_size = min(window_size, len(data))
    while count < window_size:
        p = packet(receiver_port, seq, ACK, 0, 0, 0, data[count])
        if random.random() > pdrop:
            # packet is sent
            client_socket.sendto(p.byte_packet, address)
            generate_write(log_txt, pass_time, "snd", 'D', p.seq, p.data, p.ACK)

        else :
            # packet is loss
            generate_write(log_txt, pass_time, "drop", 'D', p.seq, p.data, p.ACK)

        seq = seq + len(data[count])
        count = count + 1

    received_line = 0

    while received_line < window_size:
        try:
            packet_received, address = client_socket.recvfrom(2048)
            received_packet = unpack(packet_received)

            generate_write(log_txt, pass_time, "rcv", 'A', received_packet.seq, received_packet.data, received_packet.ACK)

            received_line = received_line + 1

            if received_packet.ACK > last_received_ACK:
                # Remove received data
                data.pop(0)
                last_received_ACK = received_packet.ACK
        except OSError:
            seq = last_received_ACK
            seq, ACK, last_received_ACK = pass_packet(data, window_size, seq, ACK, pdrop, address, client_socket, log_txt, last_received_ACK, MSS)
            break
    return (seq, ACK, last_received_ACK)

if __name__ == '__main__':

    receiver_host_ip = sys.argv[1]
    # the IP address of the host machine on which the Receiver is running.
    receiver_port = int(sys.argv[2])
    # the port number on which Receiver is expecting to receive packets from the sender. 
    # This should match the command line argument of the same name for the Receiver.
    fileToSend = sys.argv[3]
    # the name of the text file that has to be transferred from sender to receiver using your reliable transport protocol. 
    # You may assume that the file included in the argument will be available in the current working directory of the Sender with the correct access permissions set (read).
    MWS = int(sys.argv[4])
    # the maximum window size used by your PTP protocol in bytes.
    MSS = int(sys.argv[5])
    # Maximum Segment Size which is the maximum amount of data (in bytes) carried in each PTP segment. 
    # NOTE: In our tests we will ensure that MWS is exactly divisible by MSS.
    timeout = int(sys.argv[6])
    # the value of timeout in milliseconds.
    pdrop = float(sys.argv[7])
    # the probability that a PTP data segment which is ready to be transmitted will be dropped. 
    # This value must be between 0 and 1. 
    seed = int(sys.argv[8])
    # The seed for your random number generator. 


    sender(receiver_host_ip, receiver_port, fileToSend, MWS, MSS, timeout, pdrop, seed)

