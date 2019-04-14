from ipykernel.kernelbase import Kernel
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import urllib 
import base64
import requests
import socket

login = ""
password = ""

class Connection():
    def request_cmd(code):
        ''' Send code execution request to a server
        Args:
            code: commands to be executed.

        Returns:
            Server response string
        ''' 
        host = "127.0.0.1"
        port = 9090

        open('log.txt','a').write("Prepare data for netty\n")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host,port))
        client.send(bytes(code, 'utf-8'))
        open('log.txt','a').write("Sent comands request\n")
        response = client.recv(4096)
        open('log.txt','a').write("Got response from netty"+response.decode('utf-8')+"\n")
        return response.decode('utf-8')


class Handler(BaseHTTPRequestHandler):
    out = None
    def do_GET(self):
        global login
        global password
        login, password = self.path[1:].split('&')
        open('log.txt','a').write("Got login password from Jupyter cell\n")
        if (Connection.request_cmd("login "+login+" "+password) == "Success"):
            self.send_response(200)
        else:
            self.send_response(400)
        self.send_header('Content-type', 'text')
        self.send_header("Content-Length", str(len("Oh hi Mark")))
        self.send_header("Access-Control-Allow-Origin", "*") 
        self.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin") 
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept") 
        self.end_headers()
        self.wfile.write("Oh hi Mark".encode("UTF-8"))

        
class GeoKernel(Kernel):
    implementation = 'GEO'
    implementation_version = '1.0'
    language = 'geo' 
    language_version = '1.0'
    language_info = {'name': 'geo',
                     'mimetype': 'text/x-geo',  # mimetype for script files in this language
                     'codemirror_mode': 'geo',
                     'extension': '.geo'}
    banner = "GEO Console"

    '''
    httpd = HTTPServer(('127.0.0.1', 9099), Handler)
    httpd_active = False
    if not self.httpd_active:
            self.httpd.serve_forever()
            self.httpd_active = True
    '''

    commands = ["create", "show", "delete", "update", "login"]
    subCommands = ["layer", "map"]
    inspections = {
        "create" : "creates new object",
        "update" : "updates new object",
        "show map" : "returns an html document containing the map with all it's layers\n map_name:string",
        "create map" : "name:string x:double y:double zoom:int",
        "update map" : "name:string new_name:string",
        "create layer" : "name:string layer:string",
    }


    def do_log(self, text):
        open('log.txt','a').write(text)

    def do_complete(self, code, cursor_pos):
        self.do_log('do_complete \n') #str(code) + str(cursor_pos)
        matches = []
        last_command = code[:cursor_pos].split("\n")[-1].strip().split(" ")[-1]
        if last_command in self.commands:
            matches = self.subCommands
        elif last_command in self.subCommands:
            matches = self.commands
        if code[cursor_pos-1] != " ":
            matches = [" "+i for i in matches]
        return {
            'status' : 'ok',
            'cursor_start' : cursor_pos,
            'cursor_end' : cursor_pos,
            'matches' : matches}

    def do_inspect(self, code, cursor_pos, detail_level=0):
        self.do_log("do_inspect \n")
        commands = code[:cursor_pos].split("\n")[-1].strip()
        if len(commands.split()) > 2:
            commands = " ".join(commands.split()[:2])
        inspection = self.inspections.get(commands)
        if inspection == None:
            inspection = commands
        content = {
            'status': 'ok',
            'found': True,
            'data': {'text/plain':inspection},
            'metadata': {}}

        return content

    def login_request(self):
        data = "<html><style>/* Bordered form */form{border: 3px solid #f1f1f1;}/* Full-width inputs */input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */button{background-color: #4CAF50; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */button:hover{opacity: 0.8;}/* Extra style for the cancel button (red) */.cancelbtn{width: auto; padding: 10px 18px; background-color: #f44336;}/* Center the avatar image inside this container */.imgcontainer{text-align: center; margin: 24px 0 12px 0;}/* Avatar image */img.avatar{width: 40%; border-radius: 50%;}/* Add padding to containers */.container{padding: 16px;}/* The \"Forgot password\" text */span.psw{float: right; padding-top: 16px;}/* Change styles for span and cancel button on extra small screens */@media screen and (max-width: 300px){span.psw{display: block; float: none;}.cancelbtn{width: 100%;}}</style> <div class=\"container\"> <label for=\"uname\"><b>Username</b></label> <input type=\"text\" id=\"loginInput\" placeholder=\"Enter Username\" name=\"uname\" required> <label for=\"psw\"><b>Password</b></label> <input type=\"password\" id=\"passwordInput\" placeholder=\"Enter Password\" name=\"psw\" required> </div><button onclick=\"myFunction()\">Login</button> <p id=\"result\"> hi</p><script type=\"text/javascript\">function myFunction(){var login=document.getElementById(\"loginInput\").value; var password=document.getElementById(\"passwordInput\").value; var http=new XMLHttpRequest(); var params=login+'&'+password; var url='http://127.0.0.1:9099/'+params; http.open('GET', url, true); http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded'); http.onprogress=function (){document.getElementById(\"result\").innerHTML=\"Checking...\"; console.log('LOADING: ', http.status);}; http.send(); http.onreadystatechange=function(){if (http.status==200) document.getElementById(\"result\").innerHTML=\"Success!\"; else document.getElementById(\"result\").innerHTML=\"Failed!\"; return;}}</script> </html>"
        self.send_html(data)        
        self.do_log("Started http server")
        return ""

    def send_html(self, data):
        self.send_response(self.iopub_socket,
            'display_data', 
            {
            'data': {'text/html' : data},
            'metadata':{}
            })

    def do_execute(self, code, silent,
                   store_history=True,
                   user_expressions=None,
                   allow_stdin=False):

        if not silent:
            server_response = Connection.request_cmd(code)
            if "show" in code:
                # Send data to be displayed in a cell
                self.send_html(server_response)
            else:
                # Send the output to the client
                self.send_response(
                    self.iopub_socket,
                    'stream', {
                        'name': 'stdout',
                        'text':server_response,
                        'data': {
                                #'text/html' : server_response
                            }
                        })
        # Return the exection results
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class = GeoKernel)