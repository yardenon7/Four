
import os.path
import socket

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2
DEFAULT_URL = "/index.html"
REDIRECTION_DICTIONARY = {"/forbidden": "403 FORBIDDEN", "/error": "500 INTERNAL SERVER ERROR"}
MAX_PACKET=102400
WEB_ROOT = "C:/Users/Public/pythonProject1/webroot"
MOVED_RESPONSE = b'HTTP/1.1 302 MOVED TEMPORARILY\r\nLocation: /\r\n\r\n'
ERROR_404 = b'HTTP/1.1 404 Not Found\r\n\r\n'
ERROR_400= b'HTTP/1.1 400 BAD REQUEST\r\n\r\n'


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """
    file_path = WEB_ROOT + file_name
    source_file = open(file_path, 'rb')
    data = source_file.read()
    source_file.close()
    return data


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    """ """
    # TO DO : add code that given a resource (URL and parameters) generates
    # the proper response

    if resource == '/':
        uri = DEFAULT_URL
    else:
        uri = resource

    if uri == "/moved":
        http_response = MOVED_RESPONSE

    elif uri in REDIRECTION_DICTIONARY.keys():
        response = f"HTTP/1.1 {REDIRECTION_DICTIONARY[uri]}\r\n\r\n"
        client_socket.send(response.encode())
        return

    elif not os.path.isfile(WEB_ROOT + uri):
        client_socket.send(ERROR_404)
        client_socket.close()
        return
    # TO DO: check if URL had been redirected, not available or other error
    # code. For example:
        # TO DO: send 302 redirection response

    else:
        response_line = "HTTP/1.1 200 OK\r\n"
        http_header = ''
        # TO DO: extract requested file tupe from URL (html, jpg etc)
        file_type = uri.split(".")[-1]
        if file_type == 'html':
            http_header = "Content-Type: text/html; charset=utf-8\r\n"
        elif file_type == 'jpg':
            http_header = "Content-Type: image/jpeg\r\n"
        elif file_type == 'css':
            http_header = "Content-Type: text/css\r\n"
        elif file_type == 'js':
            http_header = "Content-Type: text/javascript; charset=UTF-8\r\n"
        elif file_type == 'txt':
            http_header = "Content-Type: text/plain\r\n"
        elif file_type == 'ico':
            http_header = "Content-Type: image/x-icon\r\n"
        elif file_type == 'gif':
            http_header = "Content-Type: image/jpeg\r\n"
        elif file_type == 'png':
            http_header = "Content-Type: image/x-icon\r\n"

        # TO DO: read the data from the file
        data = get_file_data(uri)
        http_header = http_header + "Content-Length:" + str(len(data)) + "\r\n\r\n"
        http_response = response_line.encode() + http_header.encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    cmd = request.split(' ')
    if len(cmd)<3:
        return False, ""
    if cmd[0] != 'GET' or cmd[2][:10] != 'HTTP/1.1\r\n':
        return False, ""
    return True, cmd[1]


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        try:
            client_request = client_socket.recv(MAX_PACKET).decode('utf-8')
            while client_request[-4:] != '\r\n\r\n':
                client_request += client_socket.recv(MAX_PACKET).decode('utf-8')  # Decode bytes to string

            valid_http, resource = validate_http_request(client_request)

            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket)
                break  # Exit the loop after handling a valid request
            else:

                print('Error: Not a valid HTTP request')
                client_socket.send(ERROR_400)
                break  # Exit the loop if the request is invalid

        except ConnectionError:
            print('Client disconnected unexpectedly')
            break
        finally:
            print('Closing connection')
            client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
