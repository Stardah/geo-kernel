import re
import sys


class Inspector:
    REG_EX_GDAL = '(gdal)\w+.*'
    # To show constant values of argument (1: obj) (2: command) (3: all args)...
    REG_EX_OBJ_CMD_ARGS = '(\w+)\s(\w+)\s(.*-+\w+.*)'
    # To show constant values of argument (1: obj) (2: command)
    REG_EX_OBJ_COMMAND = '(\w+)\s(\w+).*'
    REG_EX_OBJ = '(\w+).*'
    NO_DATA = {
        'status': 'ok',
        'found': False,
        'data': {'text/plain': 'No description'},
        'metadata': {}}

    def __init__(self, commands):
        self.commands = commands

    def message(self, inspection):
        return {
            'status': 'ok',
            'found': True,
            'data': {'text/plain': inspection},
            'metadata': {}}

    def inspect(self, code, cursor_pos):
        self.code = code
        self.cursor_pos = cursor_pos

        last_line = code[:cursor_pos].split("\n")[-1].strip()

        # First check for gdal commands
        # If the last line contains "gdal", then we add object "gdal" at the beginning
        match = re.match(self.REG_EX_GDAL, last_line)
        if match is not None:
            last_line = 'gdal ' + last_line

        # If user looks for an argument's description
        # we check the "Object command args" match
        match = re.match(self.REG_EX_OBJ_CMD_ARGS, last_line)
        if match is not None:
            return self.inspect_arg(match)

        # If user looks for a command's description
        # we check the "Object command" match
        match = re.match(self.REG_EX_OBJ_COMMAND, last_line)
        if match is not None:
            return self.inspect_command(match)

        # If user looks for an object's description
        # we check the "Object" match
        match = re.match(self.REG_EX_OBJ, last_line)
        if match is not None:
            return self.inspect_obj(match)

        # Found nothing
        return self.NO_DATA

    def inspect_arg(self, match):
        # So the first group is an object, the second is a command
        # and then N words of arguments and it's values
        obj = match.group(1)
        command = match.group(2)
        try:
            # Find last argument without keeping list of matches
            for last_arg in re.finditer(r"(-+\w+)", match.group(3)):
                pass
            last_arg = self.commands[obj]['commands'][command]['args'][last_arg.group(1)]
            return self.message(last_arg['description'])
        except:
            # Given pair of object and command does not exist
            return self.NO_DATA

    def inspect_command(self, match):
        # So the first group is an object, the second is a command
        obj = match.group(1)
        command = match.group(2)
        try:
            desc = self.commands[obj]['commands'][command]['description']
            return self.message(desc)
        except:
            # Given pair object-command doen not exist
            return self.NO_DATA

    def inspect_obj(self, match):
        # So the first group is an object
        obj = match.group(1)
        try:
            commands = self.commands[obj]['description']
            return self.message(commands)
        except:
            # Given object doen not exist
            return self.NO_DATA