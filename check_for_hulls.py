#!/usr/bin/env python3

import datetime
import bgtunnel
import MySQLdb
import re
from emailer import *
from dotenv import load_dotenv

load_dotenv()


#### HEAR BE DRAGONS
def push_sheet(xlshulls):
    forwarder = bgtunnel.open(ssh_user=os.getenv('SSH_USER'), ssh_address=os.getenv('SSH_HOST'), host_port=3306, bind_port=3307)
    #forwarder = bgtunnel.open(ssh_user=os.getenv('SSH_USER'), ssh_address='10.10.200.93', host_port=3306, bind_port=3306)

    conn= MySQLdb.connect(host='127.0.0.1', port=3307, user=os.getenv('DB_USER'), passwd=os.getenv('DB_PASS'), db=os.getenv('DB_NAME'))

    conn.query("""TRUNCATE TABLE wp_nrb_hulls""")
    r=conn.use_result()

    cursor = conn.cursor()
    sql = """
    INSERT INTO wp_nrb_hulls (
        hull_serial_number, dealership, model,
        last_name, first_name, phone,
        mailing_address, mailing_city, mailing_state, mailing_zip,
        street_address, street_city, street_state, street_zip,
        date_purchased, p
    ) VALUES (
        %s, %s, %s, 
        %s, %s, %s, 
        %s, %s, %s, %s, 
        %s, %s, %s, %s, 
        %s, %s
    )"""
    cursor.executemany(sql,sorted(xlshulls[:1287]))
    conn.commit()

    cursor.close()
    conn.close()
    forwarder.close()


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
        xlshulls, errors_dealer, errors_boat_model, errors_hull = readsheet(xlsfile)
        push_sheet(xlshulls)
        if (errors_dealer or errors_boat_model or errors_hull):
            body = format_errors(errors_dealer, errors_boat_model, errors_hull)
            mail_results('Dealer Inventory Data Entry Errors', body)
    except OSError:
        mail_results(
            'Registrations and Dealer Inventory Sheet is Open',
            'Registrations and Dealer Inventory Sheet is Open, website can not be updated'
        )
    except Exception as e:
        mail_results(
            'Registrations and Dealer Inventory Sheet Processing Error',
            '<p>Website can not be updated due to error on sheet:<br />\n' + e + '</p>'
        )

if __name__ == "__main__":
    main()
