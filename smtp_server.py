# STMP server
mails = {}

import asyncio
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink, Mailbox, Message
from email.message import Message as Em_Message
from aiosmtpd.smtp import Envelope as SMTPEnvelope
from aiosmtpd.smtp import Session as SMTPSession
from aiosmtpd.smtp import SMTP as SMTPServer

class ExampleHandler(Message):
    def __init__(self):
        logger.info("Starting SMTP server")
        super().__init__()
        self.mails = []

    def handle_message(self, message: Em_Message) -> None:
        print("Message received")
        print(message)
        self.mails.append(message)


async def smtp_server():
#    cont = Controller(Mailbox('/Users/jan/tmp/mails'), hostname='', port=8025)
    cont = Controller(ExampleHandler(), hostname='localhost', port=8025)
    cont.start()
