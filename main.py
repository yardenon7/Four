import os.path
import socket

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2
DEFAULT_URL = "/index.html"
REDIRECTION_DICTIONARY = {"/forbidden": "403 FORBIDDEN", "/error": "500 INTERNAL SERVER ERROR"}
MAX_PACKET = 102400
WEB_ROOT = "C:/Users/Public/pythonProject1/webroot"
MOVED_RESPONSE = b'HTTP/1.1 302 MOVED TEMPORARILY\r\nLocation: /\r\n\r\n'
ERROR_404 = b'HTTP/1.1 404 Not Found\r\n\r\n'
ERROR_400 = b'HTTP/1.1 400 BAD REQUEST\r\n\r\n'


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


def handle_client_request(resource, client_socket, kind_of_request, headers):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param kind_of_request:
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    """ """
    # TO DO : add code that given a resource (URL and parameters) generates
    # the proper response
    http_header = ''
    data = ''
    http_response = ''
    if resource == '/':
        uri = DEFAULT_URL
    else:
        uri = resource

    if uri == "/moved":
        http_response = MOVED_RESPONSE

    elif kind_of_request == 'POST' and uri.split('=')[0] == '/upload?file-name':
        try:
            filename = uri.split('=')[1]  # Assuming format: /upload?file-name=filename.ext
            data = client_socket.recv(MAX_PACKET)
            while len(data) < int((headers[1])):
                data += client_socket.recv(MAX_PACKET)  # Receive until the end of the request

            full_path = 'upload' + '/'+ filename
            with open(full_path, "wb") as file:
                file.write(data)


            http_response = b"HTTP/1.1 200 OK\r\n\r\n"
            client_socket.send(http_response)
            return

        except Exception as e:  # Handle any errors during file reception or saving
            print(f"Error handling upload: {e}")
            client_socket.send(ERROR_400)
            return

    elif uri.split('=')[0] == 'image?image-name':
        try:
            file_path = 'upload/' + uri.split('=')[1]
            with open(file_path, 'rb') as f:
                data = f.read()
        except Exception:
            client_socket.send(ERROR_400)
            return



    elif uri.split('=')[0] == "/calculate-next?num":
        try:
            num = int(uri.split('=')[-1])
            http_header = "Content-Type: text/plain\r\n"
            data = (str(num + 1)).encode()
        except ValueError or KeyboardInterrupt:
            client_socket.send(ERROR_400)
            return

    elif uri.split('?')[0] == "/calculate-area" and (
            uri.split('?')[-1].split('&')[0].split('=')[0] == 'height' or uri.split('?')[-1].split('&')[0].split('=')[0]
            == 'width') and (
            uri.split('?')[-1].split('&')[-1].split('=')[0] == 'width' or
            uri.split('?')[-1].split('&')[-1].split('=')[0] == 'height'):
        try:
            params = uri.split('?')[1].split('&')
            height = float(params[0].split('=')[-1])  # Extract height
            width = float(params[1].split('=')[-1])  # Extract width
            http_header = "Content-Type: text/plain\r\n"
            data = (str(0.5 * width * height)).encode()
        except ValueError or KeyboardInterrupt:
            client_socket.send(ERROR_400)
            return
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
        http_header = ''
        # TO DO: extract requested file type from URL (html, jpg etc)
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
        data = get_file_data(uri)
        # TO DO: read the data from the file
    if not uri == "/moved":
        response_line = "HTTP/1.1 200 OK\r\n"
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
    if len(cmd) < 3:
        return False, "", '', []
    if (cmd[0] != 'GET' and cmd[0] != 'POST') or cmd[2][:10] != 'HTTP/1.1\r\n':
        return False, "", '', []
    if cmd[0] == 'GET':
        return True, cmd[1], cmd[0], []
    content_type=''
    content_length=''
    for i in range(len(cmd)):
        if cmd[i].endswith("Content-Type:"):
            content_type = cmd[i+1]
            content_type = content_type[:content_type.find("\r\n")]
        if cmd[i].endswith("Content-Length:"):
            content_length =cmd[i+1]
            content_length = content_length[:content_length.find("\r\n")]
    return True, cmd[1], cmd[0], [content_type, content_length]

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

            valid_http, resource, kind_of_request, headers = validate_http_request(client_request)

            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket, kind_of_request, headers)
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
