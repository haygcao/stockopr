import http.client, urllib.parse
import json
diag1 = {'aaa': '111'}
data = json.dumps(diag1)

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
conn = http.client.HTTPConnection('localhost', 8888)
conn.request('POST', '/ippinte/api/scene/getall', data.encode('utf-8'), headers)
response = conn.getresponse()

stc1 = response.read().decode('utf-8')
stc = json.loads(stc1)

print(stc)

conn.close()
