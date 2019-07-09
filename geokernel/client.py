from websocket import create_connection
import os
import webbrowser

LOGIN_BEGIN = """<iframe width="300" height="250" srcdoc="<html><style>/* Full-width inputs */ input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}/* Set a style for all buttons */ button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}/* Add a hover effect for buttons */ button:hover{opacity: 0.8;}</style> <div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Login</button> <div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function (event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; var token='"""
LOGIN_END = """'; websocket.send('login '+login+' '+password+' '+token);}; websocket.onmessage=function (event){value.textContent=event.data;}; </script> </html>" frameborder="0" allowfullscreen=""></iframe>"""
REGISTER_BEGIN = """<iframe width="300" height="250" srcdoc="<html><style>input[type=text], input[type=password]{width: 100%; padding: 12px 20px; margin: 8px 0; display: inline-block; border: 1px solid #ccc; box-sizing: border-box;}button{background-color: #4e91fc; color: white; padding: 14px 20px; margin: 8px 0; border: none; cursor: pointer; width: 100%;}button:hover{opacity: 0.8;}</style><div class='container'> <label for='uname'><b>Username</b></label> <input type='text' id='loginInput' placeholder='Enter Username' name='uname' required> <label for='psw'><b>Password</b></label> <input type='password' id='passwordInput' placeholder='Enter Password' name='psw' required> </div><button class='check'>Register</button><div class='state'> Result: <span class='value'>?</span> </div><script type='text/javascript'> var url='ws://127.0.0.1:9090/'; var check=document.querySelector('.check'), value=document.querySelector('.value'), websocket=new WebSocket(url); check.onclick=function(event){var login=document.getElementById('loginInput').value; var password=document.getElementById('passwordInput').value; document.getElementById('passwordInput').value=''; var token='"""
REGISTER_END = """'; websocket.send('register ' + login + ' ' + password + ' ' + token);}; websocket.onmessage=function(event){value.textContent=event.data;};</script></html>" frameborder="0" allowfullscreen=""></iframe>"""
SERVER_URL = 'ws://localhost:9090/'

token = ''


class Client:

    @staticmethod
    def request_ws(code):
        """ Send code execution request to a server
                Args:
                    code: commands to be executed.

                Returns:
                    Server response string
        """
        try:
            ws = create_connection(SERVER_URL)
            ws.send(code)
            result = ws.recv()
            ws.close()
            if 'token' in code:
                global token
                token = result
            return result
        except Exception as e:
            return e

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
        token = Client.request_ws("token")
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
        token = Client.request_ws("token")
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
