from ipykernel.kernelbase import Kernel
import json
from .commands import Commands
from .client import Client, do_log


class GeoKernel(Kernel):
    # Kernel info
    implementation = 'GEO'
    implementation_version = '0.1'
    language = 'geo'
    language_version = '1.0'
    language_info = {'name': 'geo',
                     'mimetype': 'text/x-geo',  # mimetype for script files in this language
                     'codemirror_mode': 'geo',
                     'extension': '.geo'}
    banner = "GEO Console"

    def __init__(self, **kwargs):
        self.ip = '127.0.0.1'
        self.port = '8080'
        from jupyter_client.kernelspec import KernelSpecManager
        destination = KernelSpecManager()._get_destination_dir('geo', user=True, prefix=None)
        with open(destination+'\config.txt', 'r') as f:
            do_log(destination+'\config.txt')
            self.port = f.readline().split('=')[1].strip()
            self.ip = f.readline().split('=')[1].strip()

        self.client = Client(self.port, self.ip)
        super().__init__(**kwargs)

    def do_complete(self, code, cursor_pos):
        matches = []
        last_line = code[:cursor_pos].split("\n")[-1].strip()
        words = last_line.split()
        length = len(words)
        # Process gdal commands
        if "gdal" in last_line:
            # User requested command's arguments
            if length == 1:
                matches = Commands.getArgs("gdal", words[0])
            # User requested argument's valid values
            else:
                matches = Commands.getGdalArgValues(words[-1])
        # Line contains an object and a command
        # thus, we should return command's arguments
        elif length > 1:
            obj, command = last_line.split()[:2]
            matches = Commands.getArgs(obj, command)
        # Line contains only an object
        elif length == 1:
            matches = Commands.getCommands(words[0])

        if code[cursor_pos - 1] != " ":
            matches = [" " + i for i in matches]
        return {
            'status': 'ok',
            'cursor_start': cursor_pos,
            'cursor_end': cursor_pos,
            'matches': matches}

    def do_inspect(self, code, cursor_pos, detail_level=0):
        commands = code[:cursor_pos].split("\n")[-1].strip()
        if "gdal" in commands:
            commands = commands.split()[0]
        elif len(commands.split()) > 1:
            commands = " ".join(commands.split()[:2])
        inspection = Commands.inspections.get(commands)
        if inspection is None:
            inspection = commands
        content = {
            'status': 'ok',
            'found': True,
            'data': {'text/plain': inspection},
            'metadata': {}}

        return content

    def send_html(self, data):
        """ Send message with html data to the frontend via iopub socket
            Args:
                data: any data to be sent as an html.
        """
        self.send_response(self.iopub_socket, 'display_data',
                           {
                               'data': {'text/html': data},
                               'metadata': {}
                           })

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        if 'login' in code:
            self.send_html(self.client.login_request())
        elif 'register' in code:
            self.send_html(self.client.register_request())
        elif not silent:
            try:
                server_response = json.loads(self.client.request_ws(code))
                for row in server_response:
                    if row['type'] == 'html':
                        self.client.open_map(row['name'], row['data'])
                    else:
                        self.send_html(row['data'])
            except Exception as e:
                do_log(e)
            # Send data to be displayed in a cell
        # Return the execution results
        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
                }
