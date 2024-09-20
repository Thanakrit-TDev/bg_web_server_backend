import json
from flask import jsonify

print("data gen")
# time start 1711904400 change every 30S
with open('histrydata.json', 'r') as file:
    data_load = json.load(file)
    print(data_load)
