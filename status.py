import socket

def get_quake3_server_status(server_ip, server_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)  # Set a timeout for the socket

    # Quake 3 status query command
    query = b'\xff\xff\xff\xffgetstatus'

    # Send the query to the server
    server_address = (server_ip, server_port)
    try:
        print(f"Sending query to {server_ip}:{server_port}")
        sock.sendto(query, server_address)

        # Receive the response from the server
        response, _ = sock.recvfrom(4096)
        return response.decode('latin1')  # Decode the response using latin1

    except socket.timeout:
        print("Request timed out")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        sock.close()

# Example usage
server_ip = '78.46.39.20'
server_port = 7524  # Default port for Quake 3 servers
while True:
    status = get_quake3_server_status(server_ip, server_port)
    if status:
        print("Server Status:")
        #print(status)
    else:
        print("Failed to retrieve server status")
