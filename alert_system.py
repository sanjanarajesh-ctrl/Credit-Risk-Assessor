#!/usr/bin/env python3

import time
import random
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import defaultdict

# Define criteria for alerts (features)
ORDER_SPIKE_THRESHOLD = 5
ONE_SIDED_ORDER_THRESHOLD = 10
FREQUENT_LOGOUT_THRESHOLD = 3
MESSAGE_REJECTION_THRESHOLD = 4
FREQUENT_QUOTE_REQUEST_THRESHOLD = 3
HIGH_ORDER_CANCEL_THRESHOLD = 3

# FIX message tags
SENDERCOMPID = '49'
MSGTYPE = '35'
SIDE = '54'
CLORDID = '11'
LASTSHARES = '32'
HANDLINSTATE = '69'
SENDINGTIME = '52'

# Function to parse a FIX message
def parse_fix_message(message):
    fields = message.strip().split('|')
    fix_dict = {field.split('=')[0]: field.split('=')[1] for field in fields if '=' in field}
    return fix_dict

# Function to extract features from parsed FIX messages
def extract_features(fix_messages):
    data = []
    for message in fix_messages:
        fix_dict = parse_fix_message(message)
        features = {
            'client_id': fix_dict.get(SENDERCOMPID, ""),
            'msg_type': fix_dict.get(MSGTYPE, ""),
            'side': fix_dict.get(SIDE, ""),
            'clordid': fix_dict.get(CLORDID, ""),
            'lastshares': int(fix_dict.get(LASTSHARES, 0)),
            'sending_time': fix_dict.get(SENDINGTIME, ""),
            'logout': fix_dict.get(HANDLINSTATE, ""),
            'quote_request': 1 if fix_dict.get(MSGTYPE, "") == 'V' else 0,
            'order_rejection': 1 if "FIX REJECTION" in message else 0,
        }
        data.append(features)
    return pd.DataFrame(data)

# Function to train the Isolation Forest model
def train_model(normal_data):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(normal_data)
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(scaled_data)
    return model, scaler

# Function to check and generate alerts
def check_alerts(log_file_path, model, scaler):
    fix_messages = []
    alerts = defaultdict(list)
    
    with open(log_file_path, "r") as log_file:
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(1)
                continue

            fix_messages.append(line)
            if len(fix_messages) >= 100:
                features_df = extract_features(fix_messages)
                if features_df.empty:
                    continue
                
                client_ids = features_df['client_id']
                sending_times = features_df['sending_time']
                feature_values = features_df.drop(columns=['client_id', 'msg_type', 'side', 'clordid', 'sending_time', 'logout'])

                scaled_features = scaler.transform(feature_values)
                predictions = model.predict(scaled_features)

                for client_id, sending_time, prediction in zip(client_ids, sending_times, predictions):
                    if prediction == -1:  # Anomaly detected
                        alerts[client_id].append(sending_time)

                # Consolidate alerts
                for client_id, times in alerts.items():
                    unique_times = list(set(times))
                    print(f"Alert: Anomaly detected for client {client_id} at {len(unique_times)} unique times: {unique_times}")

                fix_messages = []  # Reset messages buffer

if __name__ == "__main__":
    # Generate some normal data for training the model (for demonstration purposes)
    normal_data = pd.DataFrame({
        'lastshares': [random.randint(100, 10000) for _ in range(1000)],
        'quote_request': [random.randint(0, 1) for _ in range(1000)],
        'order_rejection': [random.randint(0, 1) for _ in range(1000)]
    })
    
    model, scaler = train_model(normal_data)
    check_alerts("fix_log.txt", model, scaler)
