from websocket import create_connection
import os
import webbrowser
import json

LOGIN_BEGIN = """<html><script src='https://cdnjs.cloudflare.com/ajax/libs/jsSHA/2.0.2/sha.js'></script><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style><div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button><div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function(event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var hashObj=new jsSHA('SHA-512', 'TEXT',{numRounds: 1}); hashObj.update(password); var hash=hashObj.getHash('HEX'); document.getElementById('passwordInput').value=''; var token_='"""
LOGIN_END = """'; var data_='login ' + login + ' ' + hash; websocket.send(JSON.stringify({type: 'authenticate', token: token_, data: data_}));}; websocket.onmessage=function(event){value.textContent=event.data;};</script></html>"""
REGISTER_BEGIN = """<html><script src='https://cdnjs.cloudflare.com/ajax/libs/jsSHA/2.0.2/sha.js'></script><style>input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}button:hover{opacity: 0.8;}</style><div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Register</button><div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function(event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var hashObj=new jsSHA('SHA-512', 'TEXT',{numRounds: 1}); hashObj.update(password); var hash=hashObj.getHash('HEX'); document.getElementById('passwordInput').value=''; var token_='"""
REGISTER_END = """'; var data_='register ' + login + ' ' + hash; websocket.send(JSON.stringify({type: 'authenticate', token: token_, data: data_}));}; websocket.onmessage=function(event){value.textContent=event.data;};</script></html>"""
SERVER_URL = 'ws://localhost:9090/'

token = ''


class Client:

    @staticmethod
    def request_ws(data, type = 'code'):
        """ Send code execution request to a server
                Args:
                    code: commands to be executed.

                Returns:
                    Server response string
        """
        try:
            global token
            message = Client.encode(data, type, token)
            ws = create_connection(SERVER_URL)
            ws.send(message)
            result = ws.recv()
            ws.close()
            if 'token' == data:
                token = result
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
                do_log(exc.strerror)
                return 1

        with open(filename, 'w') as f:
            f.write(html)
        webbrowser.open_new_tab('file://'+os.path.realpath(filename))

    @staticmethod
    def login_request():
        """ Requests token and generates login form
            Returns: html login form
        """
        # request token
        token = Client.request_ws("token", "token")
        if token is not Exception:
            return LOGIN_BEGIN+token+LOGIN_END
        else:
            return token

    @staticmethod
    def register_request():
        """ Requests token and generates registration form
            Returns: shows html registration form
        """
        # request token
        token = Client.request_ws("token", "token")
        if token is not Exception:
            return REGISTER_BEGIN+token+REGISTER_END
        else:
            return token

    @staticmethod
    def prepare_code(code):
        """ Adds token to a code string
            Args: code: commands to be executed.
            Returns: String with a token to be sent to a server
        """
        global token
        return "-".join([token, code])

def do_log(text):
    """ Writes text to log file."""
    open('log.txt', 'a').write(text+"\n")
