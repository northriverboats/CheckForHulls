#!/usr/bin/env python3

import datetime
import bgtunnel
import MySQLdb
import re
from emailer import *
from dotenv import load_dotenv

load_dotenv()


#### HEAR BE DRAGONS
def check_hulls():
    forwarder = bgtunnel.open(ssh_user=os.getenv('SSH_USER'), ssh_address=os.getenv('SSH_HOST'), host_port=3306, bind_port=3307)

    conn= MySQLdb.connect(host='127.0.0.1', port=3307, user=os.getenv('DB_USER'), passwd=os.getenv('DB_PASS'), db=os.getenv('DB_NAME'))

    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(id) AS COUNT FROM wp_nrb_hulls')
    count = cursor.fetchone()

    cursor.close()
    conn.close()
    forwarder.close()

    return count[0]


def mail_results(subject, body):
    mFrom = os.getenv('MAIL_FROM')
    mTo = os.getenv('MAIL_TO')
    m = Email(os.getenv('MAIL_SERVER'))
    m.setFrom(mFrom)
    for email in mTo.split(','):
        m.addRecipient(email)
    m.addCC(os.getenv('MAIL_FROM'))
   
    m.setSubject(subject)
    m.setTextBody("You should not see this text in a MIME aware reader")
    m.setHtmlBody(body)
    m.send()

def main():
    try:
        result = check_hulls()
        if (result == 0):
            mail_results(
                'Check for Hulls Error',
                '<p>There is a problem with the website, there are no hulls listed for any dealer in wp_nrb_hulls</p>'
            )
    except Exception as e:
        mail_results(
            'Check for Hulls Error',
            '<p>There was an error while trying to count the number of hulls in wp_nrb_hulls</p>'
        )

if __name__ == "__main__":
    main()
