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

class GeoKernel(Kernel):
    # Kernel info
    implementation = 'GEO'
    implementation_version = '1.0'
    language = 'geo'
    language_version = '1.0'
    language_info = {'name': 'geo',
                     'mimetype': 'text/x-geo',  # mimetype for script files in this language
                     'codemirror_mode': 'geo',
                     'extension': '.geo'}
    banner = "GEO Console"

    # commands and its arguments for map object
    mapCommands = {"create":["-map", "-x", "-y", "-zoom"], 
    "show":["-map"], 
    "delete":["-map"], 
    "update":["-map", "-name", "-x", "-y", "-zoom"], 
    "login":[]
    }
    # commands and its arguments for layer object
    layerCommands = {"create":["-map","-layer", "-link"], 
    "show":["-layer"], 
    "delete":["-layer"], 
    "update":["-layer", "-name", "-link"], 
    "login":[]
    }
    # list of CRUD commands for both map and layer objects
    commonComands = ["create", "show", "delete", "update"]
    words = ["layer", "map"]
    # dict of commands descriptions
    inspections = {
        "map show" : "Returns an html document containing the map with all its layers\n  [-map]:string",
        "map create" : "Creates new map with name [-map]\n [-map]:string [-x]:double [-y]:double [-zoom]:int",
        "map update" : "Changes map attributes\n Required: [-map]:string\n Optional: [-name]:string [-x]:double [-y]:double [-zoom]:int",
        "map delete" : "Deletes map\n [-map]:string",
        "layer show" : "Returns a string of layer attributes",
        "layer create" : "Adds new layer [-layer] to a map [-map]\n [-layer]:string [-map]:string",
        "layer update" : "Changes layer attributes\n Required: [-layer]:string\n Optional: [-name]:string [-link]:string",
        "layer delete" : "Removes layer\n [-layer]:string"
    }

    def request_ws(self, code):
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
            return "Error"

    def do_log(self, text):
        ''' Writes text to log file
                Args: text: text to be writen.
        '''
        open('log.txt','a').write(text+"\n")

    def do_complete(self, code, cursor_pos):
        matches = []
        last_line = code[:cursor_pos].split("\n")[-1].strip()
        if len(last_line.split()) > 1:
            obj, command = last_line.split()[:2]
            if obj == "layer" and command in self.layerCommands:
                matches = self.layerCommands[command]
            elif obj == "map" and command in self.mapCommands:
                matches = self.mapCommands[command]
        elif len(last_line.split()) == 1:
            matches = self.commonComands
        if code[cursor_pos-1] != " ":
                matches = [" "+i for i in matches]    
        return {
            'status' : 'ok',
            'cursor_start' : cursor_pos,
            'cursor_end' : cursor_pos,
            'matches' : matches}

    def do_inspect(self, code, cursor_pos, detail_level=0):
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
        ''' Requests token and generates login form
            Returns: html login form
        '''
        global port
        # request token
        token = self.request_ws("token")
        if token != 'Error':
            data = """<iframe width="300" height="250" srcdoc="<html><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style> <div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button> <div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function (event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var token='"""+token+"""'; websocket.send('login '+login+' '+password+' '+token);}; websocket.onmessage=function (event){value.textContent=event.data;}; </script> </html>" frameborder="0" allowfullscreen=""></iframe>"""
            self.send_html(data)
        else:
            self.send_html(token)

    def register_request(self):
        global port
        data = """<iframe width="300" height="250" srcdoc="<html><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style> <div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button> <div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function (event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; websocket.send(login+' '+password);}; websocket.onmessage=function (event){value.textContent=event.data;}; </script> </html>" frameborder="0" allowfullscreen=""></iframe>"""
        self.send_html(data)

    def send_html(self, data):
        ''' Send message with html data to the frontend via iopub socket
                Args:
                    data: any data to be sent as an html.
        '''
        # display_data message
        self.send_response(self.iopub_socket,
            'display_data',
            {
                'data': {'text/html' : data},
                'metadata':{}
            })

    def prepare_code(self, code):
        ''' Adds token to a code string
                Args:
                    code: commands to be executed.

                Returns:
                    String with token to be sent to a server
        '''
        global token
        return "-".join([token, code])

    def do_execute(self, code, silent,
                   store_history=True,
                   user_expressions=None,
                   allow_stdin=False):

        if 'login' in code:
            self.login_request()
        elif 'register' in code:
            pass
        elif not silent:
            server_response = self.request_ws(self.prepare_code(code))
            # Send data to be displayed in a cell
            self.send_html(server_response)
        # Return the exection results
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class = GeoKernel)
