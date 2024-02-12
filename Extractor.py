#!/usr/bin/env python3


def extract_client_messages(log_file_path, client_id, output_file_path):
    client_messages = []
    
    with open(log_file_path, "r") as log_file:
        for line in log_file:
            if f'49={client_id}' in line:
                client_messages.append(line)
    
    with open(output_file_path, "w") as output_file:
        for message in client_messages:
            output_file.write(message)

    print(f"Extracted {len(client_messages)} messages for client {client_id} into {output_file_path}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extract_client_messages.py <client_id> <output_file_path>")
        sys.exit(1)

    client_id = sys.argv[1]
    output_file_path = sys.argv[2]
    
    extract_client_messages("fix_log.txt", client_id, output_file_path)
