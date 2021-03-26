import config
import time
import random
import api
import threading
import numpy as np, numpy.random
import math

def monitor_transactions(db):
    while True:
        # it's quite inefficient to query the entire transaction list again and again.
        # would be better to change the api to allow a timestamp "since" parameter to only get new transactions
        transactions = api.get_transactions()

        # check the db mapping table for any matching transactions
        deposit_addresses = db.get_deposit_addresses()
        matching_transactions = [t for t in transactions if t["toAddress"] in deposit_addresses]

        processed_transactions_set = db.get_processed_transactions()
        for t in matching_transactions:
            # check to make sure we haven't processed this transaction already
            if (t["timestamp"], t["toAddress"]) in processed_transactions_set:
                continue
            
            # process the transaction on a background thread so we don't stop monitoring transactions
            thread = threading.Thread(target=_handle_transaction, args=[t, db])
            thread.start()
            print(f"Deposit to {t['toAddress']} detected!")

        # simulated long polling
        time.sleep(5)


def _handle_transaction(transaction, db):
    # add this transaction to the db so we only process it once
    db.add_processed_transaction(transaction)

    deposit_address = transaction["toAddress"]
    amount =  transaction["amount"]
    timestamp = transaction["timestamp"]

    # send the money from the deposit address to the house account
    _send_to_house_account(deposit_address, amount)

    # take money from the house account and allocate it to the mixed addresses 
    mixed_addresses = db.get_mixed_addresses(deposit_address)
    _send_to_mixed_addresses(mixed_addresses, amount)


def _send_to_house_account(from_address, amount):
    response = api.send_jobcoins(from_address, config.HOUSE_ACCOUNT, amount)
    if not response.ok:
        raise Exception(f"Failed to send jobcoins to house account: {response.content}")
    print(f"Deposited {amount} jobcoin to the house account")


def _send_to_mixed_addresses(mixed_addresses, amount):
    # convert the amount from a string to a float
    amount = float(amount)
    
    # generate random numbers that sum to the amount using multinomial distribution in numpy
    round_down_amount = math.floor(amount) # need an integer to work with
    mixed_address_count = len(mixed_addresses)
    div_amounts = np.random.multinomial(round_down_amount, np.ones(mixed_address_count)/mixed_address_count, size=1)[0]
    
    for i in range(mixed_address_count):
        response = api.send_jobcoins(config.HOUSE_ACCOUNT, mixed_addresses[i], str(div_amounts[i]))
        if not response.ok:
            # TODO: We should record this failed transaction so that it could be replayed in the future
            raise Exception(f"Failed to send jobcoins to {mixed_addresses[i]}: {response.content}")

        print(f"Deposited {div_amounts[i]} jobcoins to {mixed_addresses[i]}")
        amount -= div_amounts[i]
        # add a random delay to increase anonymity as well as not spam the api
        time.sleep(random.randrange(5))

    # if the deposit was a decimal amount of jobcoin there will be a remainder
    # take the remainder value and put it into one of the accounts randomly
    if amount > 0:
        i = random.randrange(mixed_address_count)
        api.send_jobcoins(config.HOUSE_ACCOUNT, mixed_addresses[i], str(amount))
        print(f"Deposited {amount} jobcoins to {mixed_addresses[i]}")
