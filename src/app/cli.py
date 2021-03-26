#!/usr/bin/env python
import uuid
import sys

import click

from jobcoin_service import monitor_transactions
from database import Database
import threading

@click.command()
def main(args=None):
    print('Welcome to the Jobcoin mixer!\n')
    # initialize the in memory db which will contain our address mappings and completed transactions
    db = Database()

    # start monitoring the jobcoin transactions on a background thread so the user can continue entering in more addresses
    thread = threading.Thread(target=monitor_transactions, args=[db])
    thread.start()
    while True:
        addresses = click.prompt(
            'Please enter a comma-separated list of new, unused Jobcoin '
            'addresses where your mixed Jobcoins will be sent.\n',
            default='',
            show_default=False)
        if addresses.strip() == '':
            click.echo('\nNo address entered. Let\'s try this again...')
            continue

        addresses = addresses.split(",")
        deposit_address = uuid.uuid4().hex
        db.put_mixed_addresses(deposit_address, addresses)
        click.echo(
            '\nYou may now send Jobcoins to address {deposit_address}\nAfter a short period of time, '
            'the coins will be distributed in random amounts to your destination addresses.\n'
              .format(deposit_address=deposit_address))

if __name__ == '__main__':
    sys.exit(main())
