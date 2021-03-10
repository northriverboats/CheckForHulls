#!/usr/bin/env python3

import datetime
import bgtunnel
import MySQLdb
import re
import sys
import click
from emailer.emailer import Email
from mysql_tunnel.mysql_tunnel import TunnelSQL
from dotenv import load_dotenv


def get_current_dir():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def check_hulls(verbose):
    with TunnelSQL(verbose, cursor='DictCursor') as db:
        sql = 'SELECT COUNT(id) AS COUNT FROM wp_nrb_hulls'
        count = db.execute(sql)[0]['COUNT']

    if not verbose:
        print('Count: {}'.format(count))

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
    _ = load_dotenv(get_current_dir() + '/.env')
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
