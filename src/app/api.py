import config
import requests

# API methods
def send_jobcoins(from_address, to_address, amount):
    transaction_request = {'fromAddress' : from_address, 'toAddress' : to_address, 'amount' : amount}
    transaction_response = requests.post(config.API_TRANSACTIONS_URL, data=transaction_request)
    return transaction_response

def get_transactions():
    try:
        transactions = requests.get(config.API_TRANSACTIONS_URL).json()
        return transactions
    except Exception as e:
        # if we fail to get transactions or parse the response as json, alert the user
        raise Exception(f"Failed to retrieve jobcoin transactions. Exception: {e}")