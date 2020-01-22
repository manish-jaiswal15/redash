""" 
    This is similar to email.py but differs from email as it is not only restricted
    to alert notifications but generally any notification to any user(or group) through Email
"""

import logging

from flask_mail import Message
from redash import mail, settings
from redash.destinations import *
from string import Template


DEFAULT_MAIL_TEMPLATE = '${query_name}'

class MailNotifier(BaseDestination):

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "addresses": {
                    "type": "string"
                },
                "subject_template": {
                    "type": "string",
                    "default": DEFAULT_MAIL_TEMPLATE,
                    "title": "Subject Template"
                }
            },
            "required": ["addresses"]
        }

    @classmethod
    def icon(cls):
        return 'fa-envelope'

    def notify(self, content, query_obj, options):
        """ 
            content is the message content to be sent to the user. It can either be a string
            or a callable with output type string
            options contains additional mail settings
        """
        recipients = [email for email in options.get('addresses', '').split(',') if email]

        if not recipients:
            logging.warning("No emails given. Skipping send.")

        try:
            if callable(content):
                html = content()
            else:
                html = html
            # finalize subject
            subject_template = options.get('subject_template', DEFAULT_MAIL_TEMPLATE)
            subject = Template(subject_template).safe_substitute(query_name=query_obj.name)
            message = Message(
                recipients=recipients,
                subject=subject,
                html=html
            )
            mail.send(message)
        except Exception as e:
            logging.exception("Couldn't send mail due to error - %s" %(str(e)))

register(MailNotifier)
