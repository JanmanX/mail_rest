import asyncio

from pop3_server import POP3Server
from smtp_server import smtp_server

if __name__ == '__main__':
    # Start SMTP
    smtp_server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(smtp_server_loop)
    smtp_server_loop.create_task(smtp_server())

    # Start POP3
    pop3_server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(pop3_server_loop)
    pop3_server = POP3Server("localhost", 1110)
    pop3_server_loop.create_task(pop3_server.start())
    try:
        smtp_server_loop.run_forever()
        pop3_server_loop.run_forever()
    except KeyboardInterrupt:
        print("User abort indicated")
    finally:
        smtp_server_loop.close()
        pop3_server_loop.close()


