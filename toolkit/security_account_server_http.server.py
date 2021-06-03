import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        data = {}
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        print(self.path)
        print('header:', self.headers, 'header end')
        print('command:', self.command, 'command end')
        req_data = self.rfile.read(int(self.headers['content-length']))
        res1 = req_data.decode('utf-8')
        res = json.loads(res1)

        data1 = {'bbb': '222'}
        data = json.dumps(data1)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))


if __name__ == '__main__':
    host = ('localhost', 8888)
    server = HTTPServer(host, SimpleHTTPRequestHandler)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
