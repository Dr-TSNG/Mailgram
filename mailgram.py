import datetime
import email
import email.header
import email.message
import email.utils
import json
import requests
import time
from imapclient import IMAPClient


startup = datetime.datetime.now()


class EmailClient(object):
    def __init__(self, protocol: str, address: str, user: str, password: str):
        if protocol != "imap":
            raise Exception("Protocol currently not supported")
        self.address = address
        self.user = user
        self.password = password

    def get_from(self, msg: email.message.Message):
        (name, addr) = email.utils.parseaddr(msg["From"])
        decode_content = email.header.decode_header(name)[0]
        if decode_content[1] is not None:
            return str(decode_content[0], decode_content[1]) + " <" + addr + ">"
        return decode_content[0] + " <" + addr + ">"

    def get_to(self, msg: email.message.Message):
        (name, addr) = email.utils.parseaddr(msg["To"])
        decode_content = email.header.decode_header(name)[0]
        if decode_content[1] is not None:
            return str(decode_content[0], decode_content[1]) + " <" + addr + ">"
        return decode_content[0] + " <" + addr + ">"

    def get_subject(self, msg: email.message.Message):
        decode_content = email.header.decode_header(msg['Subject'])[0]
        if decode_content[1] is not None:
            return str(decode_content[0], decode_content[1])
        return decode_content[0]

    def get_mail_text(self, msg: email.message.Message):
        from_ = self.get_from(msg)
        to = self.get_to(msg)
        date = msg["Date"]
        subject = self.get_subject(msg)
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_payload(decode=True).decode(
                    part.get_content_charset())

        return "From: {}\nTo: {}\nDate: {}\nSubject: {}\n\n{}".format(from_, to, date, subject, body)

    def fetch(self, exclude: list = ["Archive", "Sent", "Trash", "Drafts", "Junk"]):
        with IMAPClient(self.address) as client:
            client.login(self.user, self.password)
            folders = client.list_folders()
            for folder in folders:
                folder = folder[2]
                if any(x in folder for x in exclude):
                    continue
                client.select_folder(folder)
                messages = client.search(
                    [b'UNSEEN', b'NOT', b'DELETED', u'SINCE', startup])
                response = client.fetch(messages, 'RFC822')
                for _, data in response.items():
                    message = email.message_from_bytes(data[b"RFC822"])
                    if email.utils.parsedate_to_datetime(message["Date"]).replace(tzinfo=None) >= startup:
                        yield self.get_mail_text(message)


if __name__ == "__main__":
    with open("config.json") as config_file:
        config = json.load(config_file)
        clients = []
        for mailbox in config["mails"]:
            client = EmailClient(
                mailbox['protocol'], mailbox['address'], mailbox['user'], mailbox['password'])
            clients.append(client)
        print('Start polling')
        print('-' * 20)
        while True:
            for client in clients:
                for mail in client.fetch():
                    try:
                        print("Received mail from {}".format(client.user))
                        response = requests.post(
                            url='https://api.telegram.org/bot{}/sendMessage'.format(config['token']),
                            json={
                                'chat_id': config['chatid'],
                                'text': mail
                            },
                            proxies=config.get('proxies')
                        )
                        print(response.text)
                    except Exception as e:
                        print("Error: {}".format(e))
                    print('-' * 20)
            time.sleep(config['interval'])
