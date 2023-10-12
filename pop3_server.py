import logging
import socket
import threading
import inbox

logger = logging.getLogger(__name__)

class POP3Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages = [
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Test Message\r\n"
            b"\r\n"
            b"This is a test message body.\r\n",
        ]

        self.users = {
            "user": "password"
        }

    def start(self):
        logger.info(f"Starting POP3 server on {self.host}:{self.port}")

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            # Handle the connection in a separate thread
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        client_socket.send(b"+OK POP3 server ready\r\n")
        authenticated = False
        current_username = ""

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            command = data.decode().strip()

            if command.startswith("USER"):
                _, current_username = command.split()
                if current_username in self.users:
                    client_socket.send(b"+OK User found, enter password\r\n")
                    authenticated = False
                else:
                    client_socket.send(b"-ERR User not found\r\n")
            elif command.startswith("PASS"):
                _, password = command.split()
                if authenticated:
                    client_socket.send(b"+OK Already authenticated\r\n")
                elif current_username in self.users and self.users[current_username] == password:
                    client_socket.send(b"+OK User authenticated\r\n")
                    authenticated = True
                else:
                    client_socket.send(b"-ERR Authentication failed\r\n")
            elif command == "QUIT":
                client_socket.send(b"+OK Bye\r\n")
                client_socket.close()
                break
            elif authenticated:
                if command == "STAT":
                    num_messages = len(inbox.messages)
                    total_size = sum(len(msg.as_bytes()) for msg in inbox.messages)
                    response = f"+OK {num_messages} {total_size}\r\n"
                    client_socket.send(response.encode())
                elif command.startswith("LIST"):
                    _, message_num = command.split()
                    if message_num == "":
                        response = "+OK message list follows\r\n"
                        for i, message in enumerate(inbox.messages):
                            response += f"{i + 1} {len(message.as_bytes())}\r\n"
                        response += ".\r\n"
                        client_socket.send(response.encode())
                    else:
                        message_num = int(message_num)
                        if 1 <= message_num <= len(inbox.messages):
                            message = inbox.messages[message_num - 1]
                            response = f"+OK {message_num} {len(message.as_bytes())}\r\n"
                            client_socket.send(response.encode())
                        else:
                            client_socket.send(b"-ERR No such message\r\n")
                elif command.startswith("RETR"):
                    _, message_num = command.split()
                    message_num = int(message_num)
                    if 1 <= message_num <= len(inbox.messages):
                        message = inbox.messages[message_num - 1]
                        response = f"+OK {len(message.as_bytes())} octets\r\n"
                        response += message.as_bytes()
                        client_socket.send(response)
                    else:
                        client_socket.send(b"-ERR No such message\r\n")
                else:
                    client_socket.send(b"-ERR Command not recognized\r\n")
            else:
                client_socket.send(b"-ERR Please log in\r\n")
