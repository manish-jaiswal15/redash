""" 
    This is similar to email.py but differs from email as it is not only restricted
    to alert notifications but generally any notification to any user(or group) through Email
"""

import logging

from flask_mail import Message
from redash import mail, settings
from redash.destinations import *
from string import Template
from redash.serializers import serialize_query_result, serialize_query_result_to_csv, serialize_query_result_to_xlsx


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
                },
                "send_as_attachment": {
                    "type": "boolean",
                    "default": False
                },
                "attachment_format": {
                    "type": "string",
                    "default": "csv"
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

        mime_type = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        recipients = [email for email in options.get('addresses', '').split(',') if email]

        if not recipients:
            logging.warning("No emails given. Skipping send.")

        try:
            if callable(content):
                html = content()
            else:
                html = content
            # finalize subject
            subject_template = options.get('subject_template', DEFAULT_MAIL_TEMPLATE)
            subject = Template(subject_template).safe_substitute(query_name=query_obj.name)

            message = Message(
                recipients=recipients,
                subject=subject
            )
            if options.get('send_as_attachment', False):
                file_format = options.get('attachment_format', 'csv')
                # override and recreate
                content = globals()["serialize_query_result_to_%s" %(file_format)](html)
                message.attach('output.%s' %(file_format), mime_type["%s" %(file_format)], content)
            else:
                message.html=html

            print("Subject - %s" %(subject))

            mail.send(message)
        except Exception as e:
            logging.exception("Couldn't send mail due to error - %s" %(str(e)))

register(MailNotifier)
