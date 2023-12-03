import socket
import struct

# Define the IGMP message types
IGMP_TYPE_QUERY = 1
IGMP_TYPE_REPORT = 2

# Define the IGMP group address
IGMP_GROUP_ADDRESS = "224.0.0.0"

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IGMP group address
sock.bind((IGMP_GROUP_ADDRESS, 0))

# Set the IP_MULTICAST_TTL option to 1
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

# Join the IGMP group
sock.sendto(struct.pack("!BB", IGMP_TYPE_REPORT, 0), (IGMP_GROUP_ADDRESS, 0))

# Receive IGMP messages
while True:
    data, addr = sock.recvfrom(1024)

    # Unpack the IGMP message
    type, group_address = struct.unpack("!BB", data[:2])

    # Print the IGMP message
    print("IGMP message received:", type, group_address)
