from websocket import create_connection, WebSocketConnectionClosedException
import os
import webbrowser
import json
import ssl

LOGIN_BEGIN = """<html><script src='https://cdnjs.cloudflare.com/ajax/libs/jsSHA/2.0.2/sha.js'></script><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style><div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button><div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='"""
LOGIN_NEXT = """'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function(event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var hashObj=new jsSHA('SHA-512', 'TEXT',{numRounds: 1}); hashObj.update(password); var hash=hashObj.getHash('HEX'); document.getElementById('passwordInput').value=''; var token_='"""
LOGIN_END = """'; var data_='login ' + login + ' ' + hash; websocket.send(JSON.stringify({type: 'authenticate', token: token_, data: data_}));}; websocket.onmessage=function(event){value.textContent=event.data;};</script></html>"""
REGISTER_BEGIN = """<html><script src='https://cdnjs.cloudflare.com/ajax/libs/jsSHA/2.0.2/sha.js'></script><style>input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}button:hover{opacity: 0.8;}</style><div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Register</button><div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='"""
REGISTER_NEXT = """'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function(event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var hashObj=new jsSHA('SHA-512', 'TEXT',{numRounds: 1}); hashObj.update(password); var hash=hashObj.getHash('HEX'); document.getElementById('passwordInput').value=''; var token_='"""
REGISTER_END = """'; var data_='register ' + login + ' ' + hash; websocket.send(JSON.stringify({type: 'authenticate', token: token_, data: data_}));}; websocket.onmessage=function(event){value.textContent=event.data;};</script></html>"""


class Client:

    def __init__(self, port, ip):
        print(port)
        print(ip)
        self.url = 'wss://'+ip+':'+port+'/'
        self.token = ''

    def request_ws(self, data, type = 'code'):
        """ Send code execution request to a server
                Args:
                    code: commands to be executed.

                Returns:
                    Server response string
        """
        try:
            message = Client.encode(data, type, self.token)
            ws = create_connection(self.url, sslopt={"cert_reqs": ssl.CERT_NONE})
            ws.send(message)
            result = ws.recv()
            ws.close()
            if 'token' == data:
                self.token = result
            return result
        except Exception as e:
            return e

    @staticmethod
    def encode(data, type, token):
        message = {
            "type": type,
            "token": token,
            "data": data
        }
        return json.dumps(message)

    @staticmethod
    def open_map(map_name, html):
        filename = './maps/'+map_name+'.html'
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                #do_log(exc.strerror)
                return 1

        with open(filename, 'w') as f:
            f.write(html)
        webbrowser.open_new_tab('file://'+os.path.realpath(filename))

    def login_request(self):
        """ Requests token and generates login form
            Returns: html login form
        """
        # request token
        self.token = self.request_ws("token", "token")
        if self.token is not WebSocketConnectionClosedException:
            return LOGIN_BEGIN+self.url+LOGIN_NEXT+self.token+LOGIN_END
        else:
            self.token = str(self.token)
            return self.token

    def register_request(self):
        """ Requests token and generates registration form
            Returns: shows html registration form
        """
        # request token
        self.token = self.request_ws("token", "token")
        if self.token is not Exception:
            return REGISTER_BEGIN+self.url+REGISTER_NEXT+self.token+REGISTER_END
        else:
            self.token = str(self.token)
            return self.token

def do_log(text):
    """ Writes text to log file."""
    open('log.txt', 'a').write(text+"\n")
