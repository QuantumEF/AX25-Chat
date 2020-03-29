#!/usr/bin/python
import sys
import socket
#from hexdump import hexdump

KISS_FEND = 0xC0    # Frame start/end marker
KISS_FESC = 0xDB    # Escape character
KISS_TFEND = 0xDC   # If after an escape, means there was an 0xC0 in the source message
KISS_TFESC = 0xDD   # If after an escape, means there was an 0xDB in the source message

class kiss_ax25:
	def __init__(self, callsign, kiss_tcp_addr="127.0.0.1", kiss_tcp_port=8001):
		self.callsign = callsign
		self.kiss_addr = kiss_tcp_addr
		self.kiss_port = kiss_tcp_port
		self.src_addr = encode_address(callsign.upper(), True)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.kiss_addr, self.kiss_port))

	def send(self, dest_call, message):
		dest_addr = encode_address(dest_call.upper(), False)
		c_byte = [0x03]           # This is a UI frame
		pid = [0xF0]              # No protocol
		msg = [ord(c) for c in message]
		packet = dest_addr + self.src_addr + c_byte + pid + msg

		# Escape the packet in case either KISS_FEND or KISS_FESC ended up in our stream
		packet_escaped = []
		for x in packet:
			if x == KISS_FEND:
				packet_escaped += [KISS_FESC, KISS_TFEND]
			elif x == KISS_FESC:
				packet_escaped += [KISS_FESC, KISS_TFESC]
			else:
				packet_escaped += [x]

		# Build the frame that we will send to Dire Wolf and turn it into a string
		kiss_cmd = 0x00 # Two nybbles combined - TNC 0, command 0 (send data)
		kiss_frame = [KISS_FEND, kiss_cmd] + packet_escaped + [KISS_FEND]
		output = bytearray(kiss_frame)
		self.s.send(output)

	def recv(self):
		recv_data = []
		message=''
		msg_bit = False
		recv_byte = self.s.recv(1)
		recv_byte = b'\x00'
		while recv_byte != KISS_FEND:
			recv_byte = ord(self.s.recv(1))
			if recv_byte == 0xF0:
				msg_bit = True
			if msg_bit:
				message+=chr(recv_byte)
			recv_data.append(recv_byte)
		raise recv_data
		source = decode_address(recv_data[1+7:8+7])
		return source, ''.join(message)

	def kill(self):
		self.s.shutdown(socket.SHUT_RD)
    	#self.s.close()

def recv_kiss():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(("127.0.0.1", 8001))
	print("Recieving")
	recv_data = []
	recv_byte = s.recv(1)
	while True:
		recv_byte = s.recv(1)
		print(recv_byte)
		if recv_byte == b'\xc0':
			#print("End of Transmission")
			break
		recv_data += recv_byte
	s.close()
	return recv_data

#Code below here slightly modified from https://thomask.sdf.org/blog/2018/12/15/sending-raw-ax25-python.html

def send_kiss(source_call, dest_call, message):
	# Make a UI frame by concatenating the parts together
	# This is just an array of ints representing bytes at this point
	dest_addr = encode_address(dest_call.upper(), False)
	src_addr = encode_address(source_call.upper(), True)
	c_byte = [0x03]           # This is a UI frame
	pid = [0xF0]              # No protocol
	msg = [ord(c) for c in message]
	packet = dest_addr + src_addr + c_byte + pid + msg

	# Escape the packet in case either KISS_FEND or KISS_FESC ended up in our stream
	packet_escaped = []
	for x in packet:
		if x == KISS_FEND:
			packet_escaped += [KISS_FESC, KISS_TFEND]
		elif x == KISS_FESC:
			packet_escaped += [KISS_FESC, KISS_TFESC]
		else:
			packet_escaped += [x]

	# Build the frame that we will send to Dire Wolf and turn it into a string
	kiss_cmd = 0x00 # Two nybbles combined - TNC 0, command 0 (send data)
	kiss_frame = [KISS_FEND, kiss_cmd] + packet_escaped + [KISS_FEND]
	output = str(bytearray(kiss_frame))
	#hexdump(bytearray(kiss_frame))
	# Connect to Dire Wolf listening on port 8001 on this machine and send the frame
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(("127.0.0.1", 8001))
	s.send(output)
	s.close()

# Addresses must be 6 bytes plus the SSID byte, each character shifted left by 1
# If it's the final address in the header, set the low bit to 1
# Ignoring command/response for simple example
def encode_address(s, final):
    if "-" not in s:
        s = s + "-0"    # default to SSID 0
    call, ssid = s.split('-')
    if len(call) < 6:
        call = call + " "*(6 - len(call)) # pad with spaces
    encoded_call = [ord(x) << 1 for x in call[0:6]]
    encoded_ssid = (int(ssid) << 1) | 0b01100000 | (0b00000001 if final else 0)
    return encoded_call + [encoded_ssid]

def decode_address(s):
	call = [chr(x>>1) for x in s[0:6]]
	ssid = str( (s[6] >> 1) & 0b11001110)
	#print(str(call)+":"+ssid)
	return ''.join(call)+'-'+ssid

#send_kiss("kn4vhm","km4yhi","hi")