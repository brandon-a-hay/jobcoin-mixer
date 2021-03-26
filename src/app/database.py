import threading

# In a real world application, I would access this data in a database
# I'm using a mutex lock to ensure the underlying data here is thread safe
class Database():
    def __init__(self):
        self.lock = threading.Lock()
        # mapping between deposit addresses and mixed addresses
        self.address_map = {}

        # keep track of all deposit addresses for quick lookups when filtering transactions
        self.deposit_addresses_set = set()

        # hash the timestamp and destination_address of a detected transaction so we only process it once
        self.processed_transactions = set()
    
    def get_deposit_addresses(self):
        with self.lock:
            return self.deposit_addresses_set

    def get_mixed_addresses(self, deposit_address):
        with self.lock:
            return self.address_map.get(deposit_address)

    def put_mixed_addresses(self, deposit_address, mixed_addresses):
        with self.lock:
            self.address_map[deposit_address] = mixed_addresses
            self.deposit_addresses_set.add(deposit_address)

    def add_processed_transaction(self, transaction):
        with self.lock:
            self.processed_transactions.add(
                (transaction["timestamp"], transaction["toAddress"])
            )
    
    def get_processed_transactions(self):
        with self.lock:
            return self.processed_transactions

