# Importing libraries
import imaplib
import email
from email.utils import parsedate_to_datetime
import logging

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[  
        logging.StreamHandler() # output to console
    ]
)
logger = logging.getLogger(__name__)

# Function to fetch unread emails from Gmail Inbox
def get_emails(mail_id = str, password = str):

    #URL for IMAP connection
    imap_url = 'imap.gmail.com'

    try:
        # Connection with GMAIL using SSL
        my_mail = imaplib.IMAP4_SSL(imap_url)

        # Logging in using your credentials
        my_mail.login(mail_id, password)

        # Selecting the Inbox to fetch messages
        my_mail.select('Inbox', readonly=False)

        #Defining Key and Value for email search
        key = 'UNSEEN'

        status, data = my_mail.uid('search', None, key) #Search for emails with specific key and value
        if status != 'OK':
            logger.error("Failed to search emails.")
            return my_mail, [], []
        
        mail_id_list = data[0].split()  # UIDs of all emails that we want to fetch 

        msgs = [] # empty list to capture all messages

        for e_uid in mail_id_list:
            typ, msg_data = my_mail.uid('fetch', e_uid, '(RFC822 INTERNALDATE)')
            internal_date = None

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    internal_date = parsedate_to_datetime(msg['Date'])  # Or fetch INTERNALDATE from flags

                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition'):
                            body = part.get_payload(decode=True)
                            if body:
                                msgs.append((e_uid, body.decode(errors="ignore"), internal_date))

        # Sorting by internal date, descending
        msgs.sort(key=lambda x: x[2], reverse=True)

        # Unpacking to get mail_ids and bodies
        mail_ids, bodies, _ = zip(*msgs) if msgs else ([], [], [])
        return my_mail, list(mail_ids), list(bodies)

    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during email fetch: {e}")
    return None, [], []

def move_to_spam(my_mail,mail_id_list):

    try:
        my_mail.select('Inbox', readonly=False)
        for e_uid in mail_id_list:
            # Copying the email to the Spam folder using UID
            result = my_mail.uid('COPY', e_uid, '[Gmail]/Spam')
            if result[0] == 'OK':
                # Marking the original message for deletion
                my_mail.uid('STORE', e_uid, '+FLAGS', r'(\Deleted)')
                logger.info(f"[COPY] Email UID {e_uid} copied to Spam and marked for deletion.")
            else:
                logger.warning(f"[COPY] Failed to copy email UID {e_uid} to Spam.")

        # Permanently deleting marked messages
        my_mail.expunge()
        logger.info("Deleted emails expunged successfully.")
    
    except Exception as e:
        logger.exception(f"Error moving emails to Spam: {e}")
    
    finally:
        # Logging out
        try:
            my_mail.logout()
            logger.info("Logged out of IMAP session.")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
    
