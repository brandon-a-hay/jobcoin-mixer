# Jobcoin Mixer
Service for making cryptocurrency transacations more anonymous

## Steps to run (using python 3):
1. Create a python virtual environment `python3 -m venv env`
2. Activate the environment `source env/bin/activate`
3. Install the dependencies using pip `pip3 install -r requirements.txt`
4. Launch the main function in cli.py and follow the prompt to add your mixed addresses.
5. Sit back and watch your jobcoin flow into your mixed addresses!

## To run tests:
- Navigate to src/ and run `python -m pytest`

## Project Structure:
- cli.py: Initializes the database, starts the transaction monitoring process, and processes the user input.
- database.py: In-memory database that stores address mappings and previously processed transactions.
- api.py: Api client that interfaces with the jobcoin api.
- jobcoin_service.py: Where most of the work happens. Monitors the jobcoin transactions, identifies incoming transactions that match our user's deposit addresses, and handles the distribution flow to the mixed addresses.

## Implementation:
- I opted for choosing a multi-threaded implementation so that this service could handle multiple deposit addresses simultaneously and process multiple transactions in parallel. To achieve this I used an in-memory database with a mutex lock for thread safety.
- As soon as the user launches the program, we start listening to jobcoin transactions.
- The user is then free to enter in as many sets of mixed addresses as they want and receive a unique deposit address as output each time.
- As soon as any incoming transactions match one of the registered deposit addresses, our transaction handler spins up in a new thread.
- The transaction handler manages the transfers to the house account and then to the mixed addresses.
- To increase anonymity, we use numpy's multinomial distribution algorithm to distribute random amounts to each mixed address.
- After the transactions complete the background thread will simply continue to monitor transactions until the user quits the program.
- I chose to not take any fees for this service. No need to be greedy!

## Future Work:
1. I currently identify an already processed transaction using a hash of the timestamp and address. Time is certainly not as reliable a construct as we would want for securing a financial app, so I would rather use a unique identifier for each transaction. In this case, the provided transactions api has no such id.
2. There's currently no way to "roll back" or replay a transaction that was partially successful. For this simple app I'm assuming the api is always available, but what if the api fails to deliver to a mixed address after successfully delivering to a previous one? To solve for this, I could use an actual database to record partially committed transactions and implement retry logic to handle recoverable api errors. A message queueing protocol could be useful here for replaying transactions and guaranteeing at least once delivery.
3. The multinomial distribution can only send different amounts if the original amount is an integer. A good next step would be to provide support for decimal values.
4. Continue adding more unit tests to cover the rest of the app functionality.