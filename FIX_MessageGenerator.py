#!/usr/bin/env python3

import random
import time
from datetime import datetime

# Define FIX message tags
CLORDID = '11'
SYMBOL = '55'
SIDE = '54'
LASTSHARES = '32'
LASTPX = '31'
MSGTYPE = '35'
SENDERCOMPID = '49'
TARGETCOMPID = '56'
HANDLINSTATE = '69'
LOGOUT = '5'
SENDINGTIME = '52'

# Define client details
CLIENT_COMPID_BASE = "CLIENT_"
GOOD_CLIENTS = ['ALEXANDER', 'BASIL', 'CARLOS', 'DIANE', 'MORGAN', 'CAMERON', 'QUINCY', 'EMERSON', 'JUSTICE', 'LENNON']
BAD_CLIENTS = ['TOMRIDDLE', 'BELLATRIX', 'URSULA', 'TREMAINE', 'VESPER']

# Define ranges for order sizes and message frequencies
ORDER_SIZE_MIN, ORDER_SIZE_MAX = 100, 10000
GOOD_MSG_FREQ = 5
BAD_MSG_FREQ = 15

# Function to generate a random FIX message
def generate_fix_message(client_id, good_client=True):
    message = "8=FIX.4.4|"

    # Sender and Target CompIDs
    message += f"{SENDERCOMPID}={CLIENT_COMPID_BASE}{client_id}|"
    message += f"{TARGETCOMPID}=SERVER_1|"

    # Unique OrderID
    message += f"{CLORDID}={random.randint(1, 1000000)}|"

    # Random Stock Symbol
    message += f"{SYMBOL}=STOCK_{random.randint(1, 100)}|"

    # Adding Sending Time
    sending_time = datetime.utcnow().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
    message += f"{SENDINGTIME}={sending_time}|"

    # Randomly choose message type
    if random.random() < 0.7:
        message_type = 'D'
    else:
        message_type = 'V'
        good_client = True

    message += f"{MSGTYPE}={message_type}|"

    if message_type == 'D':
        side = random.choice(['1', '2'])
        message += f"{SIDE}={side}|"
        last_shares = random.randint(ORDER_SIZE_MIN, ORDER_SIZE_MAX)
        message += f"{LASTSHARES}={last_shares}|"
        last_px = round(random.uniform(10, 100), 2)
        message += f"{LASTPX}={last_px}|"

        if not good_client:
            last_shares *= 2
            if random.random() < 0.2:
                message += "**FIX REJECTION: Order quantity exceeds limit|"

    if not good_client and random.random() < 0.1:
        message += f"{MSGTYPE}=5|"
        message += f"{HANDLINSTATE}={LOGOUT}|"

    checksum = 0
    for char in message:
        if char != '|':
            checksum += ord(char)
    checksum = checksum % 256
    message += f"10={checksum}|"

    return message

# Function to continuously generate messages
def generate_messages():
    with open("fix_log.txt", "a") as log_file:
        while True:
            client_id = random.choice(GOOD_CLIENTS + BAD_CLIENTS)
            is_good_client = client_id in GOOD_CLIENTS

            num_messages = BAD_MSG_FREQ if not is_good_client else GOOD_MSG_FREQ
            for _ in range(num_messages):
                fix_message = generate_fix_message(client_id, is_good_client)
                log_file.write(fix_message + "\n")
                log_file.flush()
            time.sleep(1)

if __name__ == "__main__":
    generate_messages()
