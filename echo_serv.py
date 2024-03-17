import re
import socket
from http import HTTPStatus

END_OF_STREAM = '\r\n\r\n'
HOST = "127.0.0.1"
PORT = 9999
BUFFER_SIZE = 1024


def get_request_method_and_status(data: str):
    data_line = re.search(r"(?P<method>^\w+) .*?(?P<status>\d+).+", data)
    request_method = data_line.group("method")
    request_status = int(data_line.group("status"))

    return request_method, request_status


def get_status(request_status: int = None):
    status = f'{HTTPStatus.OK} {HTTPStatus.OK.phrase}'
    if request_status in [item.value for item in list(HTTPStatus)]:
        for item in list(HTTPStatus):
            if request_status == item.value:
                status = f"{item.value} {item.phrase}"
                return status
    else:
        return status


def create_response(method: str, status: str, data: list, address):
    response_headers = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: text/html; charset=UTF-8"
        f"{END_OF_STREAM}"
    )
    client_headers = "\r\n".join(data[1:])
    response_body = (
        f"Request Method: {method}\n"
        f"Request Source: {address}\n"
        f"Response Status: {status}\n"
        f"{client_headers}"
    )
    response = response_headers.encode() + response_body.encode()

    return response


def echo_handler(connection, address):
    with connection:
        while True:
            request = connection.recv(BUFFER_SIZE)
            print("Received:", request)
            if not request:
                break
            if END_OF_STREAM.encode() in request:
                break
        data = request.decode().strip().split('\r\n')
        method, request_status = get_request_method_and_status(data[0])
        status = get_status(request_status)
        connection.send(create_response(method, status, data, address))


def start_server(host: str, port: int):
    with socket.socket() as sock:
        sock.bind((host, port))
        sock.listen()
        print(f"Server started on {host}:{port}")
        while True:
            print("Waiting for request...")
            conn, address = sock.accept()
            print(f"Request from {address}")
            echo_handler(conn, address)
            print(f"Sent response to {address}")


if __name__ == '__main__':
    start_server(HOST, PORT)
