import sys
import json

payload = open(sys.argv[1])
print(json.dumps({"payload": payload.read()}))