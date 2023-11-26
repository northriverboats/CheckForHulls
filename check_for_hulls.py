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
from envelopes import Envelope
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

def mail_results(subject, body, attachment=''):
    """ Send emial with html formatted body and parameters from env"""
    envelope = Envelope(   
        from_addr=split_address(os.environ.get('MAIL_FROM')),
        subject=subject,
        html_body=body
    )          
                   
    # add standard recepients
    tos = os.environ.get('MAIL_TO','').split(',')
    if tos[0]:         
        for to in tos:
            envelope.add_to_addr(to)
                      
    # add carbon coppies
    ccs = os.environ.get('MAIL_CC','').split(',')
    if ccs[0]:        
        for cc in ccs:
            envelope.add_cc_addr(cc)
              
    # add blind carbon copies recepients
    bccs = os.environ.get('MAIL_BCC','').split(',')
    if bccs[0]:
        for bcc in bccs:
            envelope.add_bcc_addr(bcc)
        
    if attachment:
        envelope.add_attachment(attachment)
                  
    # send the envelope using an ad-hoc connection...
    try:          
        _ = envelope.send(
            os.environ.get('MAIL_SERVER'),
            port=os.environ.get('MAIL_PORT'),
            login=os.environ.get('MAIL_LOGIN'),
            password=os.envirion.get('MAIL_PASSWORD'),
            tls=True
        )
    except SMTPException:
        click.echo("SMTP EMail error")


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
