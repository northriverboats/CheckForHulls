#!/usr/bin/env python3

"""
Send notification if number of hulls in table on website is 0
"""

import datetime
import bgtunnel
import MySQLdb
import re
import sys
import os
import click
from emailer import Email
from mysql_tunnel.mysql_tunnel import TunnelSQL
from dotenv import load_dotenv

#### HEAR BE DRAGONS
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
    mail.setPort(os.getenv('MAIL_PORT'))
    mail.setTLS(os.getenv('MAIL_TLS'))
    mail.setLogin(os.getenv('MAIL_LOGIN'))
    mail.setPassword(os.getenv('MAIL_PASSWORD'))

    mail.setFrom(mFrom)
    for email in mTo.split(','):
        mail.addRecipient(email)
    mail.addCC(os.getenv('MAIL_FROM'))

    mail.setSubject(subject)
    mail.setTextBody("You should not see this text in a MIME aware reader")
    mail.setHtmlBody(body)
    mail.send()

@click.command()
@click.option('--verbose', is_flag=True, help='show output')
@click.option('--noemail', is_flag=True, help='do not send email')
def main(verbose, noemail):

    # set python environment
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        # we are running in a normal Python environment
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # load environmental variables
    load_dotenv(dotenv_path=resource_path(".env"))

    if os.getenv('HELP'):
      with click.get_current_context() as ctx:
        click.echo(ctx.get_help())
        ctx.exit()

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
