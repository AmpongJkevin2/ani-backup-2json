import json
import sys

filename = str(sys.argv[1])

with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get top-level keys
print("ROOT KEYS:", list(data.keys()))


if len(data['backupAnime']) > 0:
    while True:
        user_input = input("Enter number: ")
        if user_input == "/q":
            exit()
        elif not user_input.isdigit():
            print("Only (number, /q)")
            continue
        user_input = int(user_input)
        keys = data['backupAnime'][user_input].keys()
        for key in keys:
            print(f"{key}: {data['backupAnime'][user_input][key]}")
