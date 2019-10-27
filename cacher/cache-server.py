import os
import socket
import redis
import time
import json

HOST = ''
PORT = 80

print("Waiting for redis server...")
time.sleep(5.0)

r = redis.Redis(host='redis', port=6379)


def process_json(data):
    try:
        j = json.loads(data)
    except json.decoder.JSONDecodeError as e:
        return json.dumps({"status": "Bad Request"})

    action = j["action"]
    if action == "put":
        res = r.get(j["key"])
        r.set(j["key"], j["message"])
        if res is not None:
            return json.dumps({"status": "Ok"})
        else:
            return json.dumps({"status": "Created"})
    elif action == "get":
        res = r.get(j["key"])
        if res is None:
            return json.dumps({"status": "Not found"})
        else:
            return json.dumps({"status": "Ok",
                               "message": res.decode('utf-8')})
    elif action == "delete":
        res = bool(r.delete(j["key"]))
        if not res:
            return json.dumps({"status": "Not Found"})
        else:
            return json.dumps({"status": "Ok"})

    return json.dumps({"status": "Bad Request"})


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen()
	conn, addr = s.accept()
	with conn:
		print("Connected by", addr)
		while True:
			data = conn.recv(1024)
			if not data:
				break
			response = process_json(data)
			# print("Got:", data)
			conn.sendall((response + '\n').encode('utf-8'))
