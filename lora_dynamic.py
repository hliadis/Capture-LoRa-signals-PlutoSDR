#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Wed Feb  2 23:46:35 2022
##################################################


from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import iio
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import lora
import socket
import threading
import time
from time import sleep
import binascii
class LoRaUDPServer():
    def __init__(self,ip,port,timeout):
        self.ip = ip
        self.port = port
        self.timeout = timeout

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.ip, self.port))
        self.s.settimeout(self.timeout)

    def __del__(self):
        self.s.close()

    def get_payloads(self):
        data = ''
        total_data = []
        while True:
            try:
                msg = self.s.recvfrom(65535)
                data = msg[0]
                address = msg[1]
                clientIP  = "Source IP Address:{}".format(address)
                print(clientIP)
                if data:
                    total_data.append(binascii.hexlify(data))
                    hex_data = total_data[0].decode("hex")
                    print "data captured: " + hex_data

                    lst = []
                    #Find the positions of the chosen delimeters and stores them on lst list.
                    for pos,char in enumerate(hex_data):
                        if(char == ' ' or char == '\n' or char == ',' or char == '\\' or char == '/'):
                            lst.append(pos)
                    
                    print("print it's item : ")
                    x = 0
                    #Iterate hex_data and split into sub-arrays based on the positions of the delimeters.
                    for i in lst:
                        print(hex_data[x:i])
                        x = i+1

                    print(hex_data[x:len(hex_data)])
            except (Exception, EOFError) as e:
                print(e)
                pass
            return total_data

class top_block(gr.top_block):

    def __init__(self,bw,sf):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.sf = sf
        self.samp_rate = samp_rate = 1000000
        self.center_freq = center_freq = 866100000
        self.bw = bw 

        ##################################################
        # Blocks
        ##################################################
        self.pluto_source_0 = iio.pluto_source("192.168.2.1", int(center_freq), int(samp_rate), int(20000000), 0x8000, True, True, True, "manual", 64, '', True)
        self.lora_message_socket_sink_0 = lora.message_socket_sink('127.0.0.1', 40868, 0)
        self.lora_lora_receiver_0 = lora.lora_receiver(1e6, center_freq, ([center_freq]), bw, sf, False, 1, True, False, False, 1, False, False)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.lora_message_socket_sink_0, 'in'))
        self.connect((self.pluto_source_0, 0), (self.lora_lora_receiver_0, 0))

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_lora_receiver_0.set_sf(self.sf)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.pluto_source_0.set_params(int(self.center_freq), int(self.samp_rate), int(20000000), True, True, True, "manual", 64, '', True)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.pluto_source_0.set_params(int(self.center_freq), int(self.samp_rate), int(20000000), True, True, True, "manual", 64, '', True)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw
    
    def set_lora_rcv(self):
        print "changing lora receiver ...\n"
        self.lora_lora_receiver_0 = lora.lora_receiver(1e6, self.center_freq, ([self.center_freq]), self.bw, self.sf, True, 1, True, False, False, 1, False, False)
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.lora_message_socket_sink_0, 'in'))
        self.connect((self.pluto_source_0, 0), (self.lora_lora_receiver_0, 0))

def run(top_global):
    mode = 1
    top_global.start()

    while True:
        #create a Datagram UDP socket and bind to loopback address and port 40868.
        udp_connection = LoRaUDPServer('127.0.0.1',40868,30)

        #Listen for incoming packets, if no packets are received within specific timeout, 
        #Exception will be thrown.
        data = udp_connection.get_payloads()

        #Closing socket
        udp_connection.__del__()

        #If incoming data occur, keep current mode sf and bandwidth.
        if (len(data) > 0):
            continue
        
        #If no data captured, change mode.
        mode = (mode + 1) % 10
        if(mode == 0):
            mode = 10
        
        print "----------Changing into mode " + str(mode) + "----------"
        sleep(0.02)
        
        #Notify current flowgraph to shutdown and wait for it to complete.
        top_global.stop()
        top_global.wait()
        
        #Initialize top block object with proper parameters based on
        #new LoRa transmission mode.
        if(mode == 1):
            top_global = top_block(125000,12)
        if(mode == 2):
            top_global = top_block(250000,12)
        elif(mode == 3):
            top_global = top_block(125000,10)
        elif(mode == 4):
            top_global = top_block(500000,12)
        elif(mode == 5):
            top_global = top_block(250000,10)
        elif(mode == 6):
            top_global = top_block(500000,12)
        elif(mode == 7):
            top_global = top_block(250000,9)
        elif(mode == 8):
            top_global = top_block(500000,9)
        elif(mode == 9):
            top_global = top_block(500000,8)
        elif(mode == 10):
            top_global = top_block(500000,7)

        #Start the new flowgraph
        sleep(0.02)
        top_global.start()

if __name__ == '__main__':
    
    global tb
    tb = top_block(125000,12)
    
    #create Thread
    thread1 = threading.Thread(target=run, args=(tb,))
    thread1.daemon = True
    thread1.start()
    
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        tb.stop()
        tb.wait()
        pass

