#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

COMMASPACE = ', '

class Mail():

    def __init__(self, smtp, sender, password, port=25, ssl=False):
        self.smtp = smtp
        self.ssl = ssl
        self.sender = sender
        self.password = password
        self.port = port
        self._content = None
        self._template = None

    def set_default_template(self):
        self._template = """\
        <html>
          <head></head>
          <body>
              <p>$title
              <br>
                $content
            </p>
          </body>
        </html>
        """

    def populate_template(self, d):
        """

        :type dictionary: dictionary
        example:
             {'title': title, 'subtitle': subtitle, 'list': '\n'.join(list)}
        """
        src = Template(self._template)
        self._content = src.substitute(d)

    def send(self, subject, recipients=[], attachments=[]):
        """ recipients are email adresses
            attachments are file patchs
        """

        # Create the enclosing (outer) message
        outer = MIMEMultipart()
        outer['Subject'] = subject
        outer['To'] = COMMASPACE.join(recipients)
        outer['From'] = self.sender
        outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

        # Record the MIME types of both parts - text/plain and text/html.
        # part1 = MIMEText(text, 'plain')
        # part2 = MIMEText(html, 'html')
        part2 = MIMEText(self._content.encode('utf-8'), 'html', 'utf-8')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        # outer.attach(part1)
        outer.attach(part2)

        # Add the attachments to the message
        for file in attachments:
            try:
                with open(file, 'rb') as fp:
                    msg = MIMEBase('application', "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
                outer.attach(msg)
            except:
                print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
                raise

        composed = outer.as_string()

        try:
            with smtplib.SMTP(self.smtp) as s:
                s.ehlo()
                if self.ssl:
                    s.starttls()  # if supported
                s.ehlo()
                if (self.password):
                    s.login(self.sender, self.password)
                s.sendmail(self.sender, recipients, composed)
                s.close()
            print("Email sent!")
        except:
            print("Unable to send the email. Error: ", sys.exc_info()[0])
            raise



if __name__ == '__main__':
   m = Mail('smtp.domain.com','alert@domain.com','')
   m.set_default_template()
   m.populate_template({'title': "test", 'content': "Test..."})
   m.send('Test',['test@abc.com','admin@abc.com'])