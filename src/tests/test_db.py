#!/usr/bin/env python
import pytest
import threading
import uuid

import sys
from app.database import Database

@pytest.fixture
def database():
    db = Database()
    return db

def test_put_deposit_addresses(database):
    # test this with multiple threads
    threads = []
    for i in range(5):
        deposit_address = uuid.uuid4().hex
        mixed_addresses = []
        for j in range(3):
            mixed_addresses.append(f"mixed_address_{i}_{j}")
        thread = threading.Thread(target=database.put_mixed_addresses, args=[deposit_address, mixed_addresses])
        threads.append(thread)
        thread.start()

    # wait for all the threads to finish
    for thread in threads:
        thread.join()
    deposit_addresses = database.get_deposit_addresses()

    # ensure all deposit addresses got inserted
    assert len(deposit_addresses) == 5
    for da in deposit_addresses:
        # ensure each deposit address is mapped to 3 mixed addresses
        mixed_addresses = database.get_mixed_addresses(da)
        assert len(mixed_addresses) == 3

def test_process_transaction(database):
    # test this with multiple threads
    fake_transactions = [{
        "timestamp": "Mar 26, 2021 9:24:19 PM",
        "toAddress": "Bob"
    },
    {
        "timestamp": "Mar 26, 2021 9:24:19 PM",
        "toAddress": "Sue"
    },
    {
        "timestamp": "Mar 26, 2021 9:24:19 PM",
        "toAddress": "John"
    }]

    threads = []
    for i in range(len(fake_transactions)):
        thread = threading.Thread(target=database.add_processed_transaction, args=[fake_transactions[i]])
        threads.append(thread)
        thread.start()

    # wait for all the threads to finish
    for thread in threads:
        thread.join()
    
    processed_transactions = database.get_processed_transactions()
    for t in fake_transactions:
        assert (t["timestamp"], t["toAddress"]) in processed_transactions
