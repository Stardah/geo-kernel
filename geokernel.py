from ipykernel.kernelbase import Kernel
from websocket import create_connection
from io import BytesIO
import urllib 
import base64
import requests
import socket

import asyncio
import json
import logging
import websockets

login = ""
password = ""
token = ""
port = 9090

class Connection():

    def request_ws(code):
        ''' Send code execution request to a server
                Args:
                    code: commands to be executed.

                Returns:
                    Server response string
        '''
        try:
            ws = create_connection("ws://localhost:9090/")
            ws.send(code)
            result = ws.recv()
            ws.close()
            if 'token' in code :
                global token
                token = result
            return result
        except Exception as e:
            open('log.txt', 'a').write(str(e) + "\n")
            return "Error"

async def client(code):
    async with websockets.connect('ws://localhost:9090') as websocket:
        await websocket.send(code)
        response = await websocket.recv()
        return response

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
        open('log.txt','a').write(text+"\n")

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
        self.do_log("do_inspect")
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
        global port
        token = Connection.request_ws("token")
        if token != 'Error':
            data = """<iframe width="300" height="300" srcdoc="<html><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style> <div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button> <div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function (event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var token='"""+token+"""'; websocket.send('login '+login+' '+password+' '+token);}; websocket.onmessage=function (event){value.textContent=event.data;}; </script> </html>" frameborder="0" allowfullscreen=""></iframe>"""
            self.send_html(data)
        else:
            self.send_html(token)

    def register_request(self):
        global port
        data = """<iframe width="300" height="300" srcdoc="<html><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style> <div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button> <div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function (event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; websocket.send(login+' '+password);}; websocket.onmessage=function (event){value.textContent=event.data;}; </script> </html>" frameborder="0" allowfullscreen=""></iframe>"""
        self.send_html(data)

    def send_html(self, data):
        #display_data
        self.send_response(self.iopub_socket,
            'execute_result',
            {
                'execution_count': self.execution_count,
                'data': {'text/html' : data},
                'metadata':{}
            })

    def prepare_code(self, code):
        global token
        return "-".join([token, code])

    def do_execute(self, code, silent,
                   store_history=True,
                   user_expressions=None,
                   allow_stdin=False):

        if 'login' in code:
            self.login_request()
        #elif 'register' in code:
        #    self.register_request()
        elif not silent:
            #rcode = self.prepare_code(code)
            server_response = Connection.request_ws(self.prepare_code(code))
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
