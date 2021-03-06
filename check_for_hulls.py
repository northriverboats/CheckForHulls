#!/usr/bin/env python3

import datetime
import bgtunnel
import MySQLdb
import re
import click
from emailer import *
from mysqltunnel import TunnelSQL
from dotenv import load_dotenv

_ = load_dotenv()


#### HEAR BE DRAGONS
def check_hulls(verbose):
    db = TunnelSQL(verbose, cursor='DictCursor')
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

@click.command()
@click.option('--verbose', is_flag=True, help='show output')
@click.option('--noemail', is_flag=True, help='do not send email')
def main(verbose, noemail):
    try:
        result = check_hulls(not verbose)
        if result == 0 and not noemail:
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
