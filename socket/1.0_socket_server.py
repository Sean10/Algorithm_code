import socket

HOST, PORT = '', 8000

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(100)
print('Serving HTTP on port %s ...' % PORT)
while True:
    client_connection, client_address = listen_socket.accept()
    while True:
        request = client_connection.recv(1024)
    #print(request.decode('utf-8'))

        #print(html)
        print(request.decode('utf-8'))


        client_connection.send(("Server received").encode("utf-8"))

    #client_connection.sendall(http_response.encode('utf-8'))
client_connection.close()
    #client_connection.close()
