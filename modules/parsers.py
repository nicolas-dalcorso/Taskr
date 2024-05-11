"""
Implementation of general purpose parsers.

nrdc
2024-04-28
v0.1.0
"""

#   Constants
#   ---------------------------------------------------------------------------

from enum import Enum;

DELIMITER__SPACE = " ";
DELIMITER__COMMA = ",";


class ParserException(BaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message);
        self.message = message;
        
    def __str__(self) -> str:
        return self.message;
    
    def __repr__(self) -> str:
        return f"ParserException(message={self.message})";
    
    def __json__(self) -> str:
        return self.__dict__();

class UserParserIntefaceStatus(Enum):
    UPI__SUCCESS                = 0;
    UPI__ERR_INVALID_INPUT      = 1;
    UPI__ERR_INVALID_OPTION     = 2;
    UPI__ERR_INVALID_FLAG       = 3;
    UPI__ERR_INVALID_COMMAND    = 4;

class UserParserInterface:
    """Acts as an interface for user input parsers.
    """
    __slots__ = ['parser', 'history', 'status', 'message', 'index', 'stack'];
    
    def __init__(self) -> None:
        self.parser = Parser([], [], [], [], []);
        self.history = [];
        self.stack = [];
        self.status = None;
        self.message = None;
        self.index = 0;
        
    def __str__(self) -> str:
        return f"UserParserInterface(parser={self.parser}, history={self.history}, status={self.status}, message={self.message})";
    
    def __repr__(self) -> str:
        return f"UserParserInterface(parser={self.parser}, history={self.history}, status={self.status}, message={self.message})";
    
    def setParser(self, parser: 'Parser') -> None:
        self.parser = parser;
        
    def setParser(self, tokens: list[str], delimiters: list[str], options: list[str], flags: list[str], commands: list[str]) -> None:
        self.parser = Parser(tokens, delimiters, options, flags, commands);
        
    def parse(self) -> str:
        try:
            current_user_input = self.parser._getUserInput();
            
            if(not current_user_input):
                raise ParserException("User input cannot be empty");
            else:
                self.stack.append(current_user_input.split(self.parser.DELIMITERS[0]));
                self.history.append((self.index, self.stack[-1]));
                self.index += 1;
                
                return self.buildAction(self.stack.pop());
        except ParserException as e:
            self.status  = UserParserIntefaceStatus.UPI__ERR_INVALID_INPUT;
            self.message = e.message;
            return self.message;
        
    def parseOption(self, option: str) -> str:
        try:
            if(option not in self.parser.OPTIONS):
                raise ParserException(f"Invalid option: {option}");
            else:
                return option;
        except ParserException as e:
            self.status  = UserParserIntefaceStatus.UPI__ERR_INVALID_OPTION;
            self.message = e.message;
            return self.message;
    
    def parseFlag(self, flag: str) -> str:
        try:
            if(flag not in self.parser.FLAGS):
                raise ParserException(f"Invalid flag: {flag}");
            else:
                return flag;
        except ParserException as e:
            self.status  = UserParserIntefaceStatus.UPI__ERR_INVALID_FLAG;
            self.message = e.message;
            return self.message;
    
    def parseCommand(self, command: str) -> str:
        try:
            if(command not in self.parser.COMMANDS):
                raise ParserException(f"Invalid command: {command}");
            else:
                return command;
        except ParserException as e:
            self.status  = UserParserIntefaceStatus.UPI__ERR_INVALID_COMMAND;
            self.message = e.message;
            return self.message;
    
    def getHistory(self) -> list[tuple[int, list[str]]]:
        return self.history;

    def buildAction(self, parsed_input: list[str]) -> str | dict[str, str]:
        action = {
            'type': None,
            'object': None,
            'options': [],
            'flags': [],
            'command': None
        };
        
        try:
            if(len(parsed_input) < 2):
                raise ParserException("InvalidInput::Parsed input must contain at least 2 elements");
            else:
                action['type'] = parsed_input[0];
                action['object'] = parsed_input[1];
                
                if(action['type'] not in self.parser.TOKENS):
                    raise ParserException(f"InvalidInput::Invalid token: {action['type']} is not a valid ACTION TYPE token.");
                elif(action['object'] not in self.parser.TOKENS):
                    raise ParserException(f"InvalidInput::Invalid token: {action['object']} is not a valid ACTION OBJECT token.");

                for token in parsed_input[2:]:
                    if("--" in token):
                        action['options'].append(token);
                    elif("-" in token):
                        action['flags'].append(token);
                    else:
                        action['command'] = token;
                
                self.parser.current_action = action;        
                
        except ParserException as e:
            self.status = UserParserIntefaceStatus.UPI__ERR_INVALID_INPUT;
            self.message = e.message;
            return self.message;
        
        
        return action;
                
    
    

class Parser:
    __slots__ = ['TOKENS', 'DELIMITERS', 'OPTIONS', 'FLAGS', 'COMMANDS', 'current_token', 'trace', 'current_action'];
    
    def __init__(self, tokens: list[str], delimiters: list[str], options: list[str], flags: list[str], commands: list[str]):
        self.TOKENS = tokens;
        self.DELIMITERS = delimiters;
        self.OPTIONS = options;
        self.FLAGS = flags;
        self.COMMANDS = commands;
        self.current_token = None;
        self.current_action = None;
        self.trace = [];
        
    def __str__(self) -> str:
        return f"Parser(tokens={self.TOKENS}, delimiters={self.DELIMITERS}, options={self.OPTIONS}, flags={self.FLAGS}, commands={self.COMMANDS})";
    
    def __repr__(self) -> str:
        return f"Parser(tokens={self.TOKENS}, delimiters={self.DELIMITERS}, options={self.OPTIONS}, flags={self.FLAGS}, commands={self.COMMANDS})";
    
    def _getUserInput(self) -> str:
        return input("> ");
    
    def execute(self):
        pass;
    
if __name__ == '__main__':
    UserParserInterface_1 = UserParserInterface();
    
    UserParserInterface_1.setParser(['new', 'task'], [DELIMITER__SPACE, DELIMITER__COMMA], ['--verbose', '--trace'], ['-t', '-y'], ['SILENT', 'STORE', 'UPDATE', 'DELETE', 'RETRIEVE']);
    
    print(UserParserInterface_1.parse());