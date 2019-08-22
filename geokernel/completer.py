import json
import re
import sys


class Completer:
    REG_EX_GDAL = '(gdal).*'

    # To show constant values of argument (1: obj) (2: command) (3: all args)...
    REG_EX_OBJ_CMD_ARGS = '(\w+)\s(\w+)(\s-+\w+(\s\"[^\"]*\"|\s\S*)?)+'
    # To show constant values of argument (1: obj) (2: command)
    REG_EX_OBJ_COMMAND = '(\w+)\s(\w+).*'
    REG_EX_OBJ = '(\w+).*'

    COMPLETE_ERROR = {
        'status': 'error',
        'cursor_start': 0,
        'cursor_end': 0,
        'matches': []}

    def __init__(self, commands):
        self.commands = commands

    def message(self, matches):
        if self.code[self.cursor_pos - 1] != " ":
            matches = [" " + i for i in matches]
        return {
            'status': 'ok',
            'cursor_start': self.cursor_pos,
            'cursor_end': self.cursor_pos,
            'matches': matches}

    def complete(self, code, cursor_pos):
        self.code = code
        self.cursor_pos = cursor_pos

        last_line = code[:cursor_pos].split("\n")[-1].strip()

        # First check for gdal commands
        # If the last line contains "gdal", then we add object "gdal" at the beginning
        match = re.match(self.REG_EX_GDAL, last_line)
        if match is not None:
            last_line = 'gdal ' + last_line

        # If user looks for an argument's constant values
        # we check the "Object command args" match
        match = re.match(self.REG_EX_OBJ_CMD_ARGS, last_line)
        if match is not None:
            result = self.complete_values(match)
            if result:
                return result

        # If user looks for a command's arguments
        # we check the "Object command" match
        match = re.match(self.REG_EX_OBJ_COMMAND, last_line)
        if match is not None:
            return self.complete_args(match)

        # If user looks for an object's commands
        # we check the "Object" match
        match = re.match(self.REG_EX_OBJ, last_line)
        if match is not None:
            return self.complete_commands(match)

        # Found nothing
        return self.COMPLETE_ERROR

    def complete_values(self, match):
        # So the first group is an object, the second is a command
        # and then N words of arguments and it's values
        obj = match.group(1)
        command = match.group(2)
        try:
            # Find last argument without keeping list of matches
            for last_arg in re.finditer(r"(-+\w+)", match.group(3)):
                pass
            last_arg = self.commands[obj]['commands'][command]['args'][last_arg.group(1)]
            if 'values' in last_arg:
                return self.message(last_arg['values'])
            # if there're no constant values then user could
            # asked for command's arguments autocomletion and just made a mistake
            return False
        except:
            # Given pair of object and command does not exist
            return self.COMPLETE_ERROR

    def complete_args(self, match):
        # So the first group is an object, the second is a command
        obj = match.group(1)
        command = match.group(2)
        if obj in self.commands:
            if command in self.commands[obj]['commands']:
                command = self.commands[obj]['commands'][command]
                if 'args' in command:
                    return self.message(list(command['args'].keys()))
                return self.COMPLETE_ERROR
            else:
                # Given command does not exist, user probably made a mistake,
                # we return list of commands for a given object
                return self.message(list(self.commands[obj]['commands'].keys()))
        else:
            # Given object doen not exist
            return self.COMPLETE_ERROR

    def complete_commands(self, match):
        # So the first group is an object
        obj = match.group(1)
        try:
            commands = list(self.commands[obj]['commands'].keys())
            return self.message(commands)
        except:
            # Given object doen not exist
            return self.COMPLETE_ERROR