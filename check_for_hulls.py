#!/usr/bin/env python3

import datetime
import bgtunnel
import MySQLdb
import re
from emailer import *
from mysqltunnel import TunnelSQL
from dotenv import load_dotenv

_ = load_dotenv()
silent = True


#### HEAR BE DRAGONS
def check_hulls():
    db = TunnelSQL(silent, cursor='DictCursor')
    sql = 'SELECT COUNT(id) AS COUNT FROM wp_nrb_hulls'
    count = db.execute(sql)[0]['COUNT']
    db.close()

    if not silent: print('Count: {}'.format(count))

    return count


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
