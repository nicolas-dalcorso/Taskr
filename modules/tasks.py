"""
Implements several classes and functions for dealing with task management.


nrdc
2024-04-28
v0.1.0
"""

from collections import namedtuple;
from enum import Enum;
from dataclasses import dataclass;
from datetime import datetime;
from modules.parsers import Parser, ParserException, UserParserInterface, UserParserIntefaceStatus;
from modules.textWrappers import wrap_text, wrap_text_with_indent, wrap_text_with_indent_and_prefix, getTags;

class TaskException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message);
        self.message = message;
        
    def __str__(self) -> str:
        return self.message;
    
    def __repr__(self) -> str:
        return f"TaskException(message={self.message})";
    
    def __json__(self) -> str:
        return self.__dict__();

class TaskStatus(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CANCELED = 4
    DELETED = 5

def getIntFromTaskStatus(status: TaskStatus) -> int:
    return status.value;

def getTaskStatusFromInt(integer: int) -> TaskStatus:
    statuses = list(TaskStatus);
    
    for status in statuses:
        if(integer == status.value):
            return status;
    
    raise TaskException(f"{integer} is not a valid `TaskStatus` (integer) value.");

def tsGet(status: TaskStatus) -> str:
    """Returns a string for the name of the `TaskStatus` value.

    Args:
        status (TaskStatus)
        
    Returns:
        str: the TaskStatus key
    """
    return status.name;

def tsSet(status_str: str) -> TaskStatus:
    return TaskStatus[status_str];

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

def getIntFromTaskPriority(priority: TaskPriority) -> int:
    return priority.value;

def getTaskPriorityFromInt(integer: int) -> TaskPriority:
    priorities = list(TaskPriority);
    
    for priority in priorities:
        if(integer == priority):
            return priority;
    return TaskPriority.URGENT;

def tpGet(priority: TaskPriority) -> str:
    return priority.name;

def tpSet(priority_str: str) -> TaskPriority:
    return TaskPriority[priority_str];

class Task:
    __slots__ = ['id', 'name', 'description', 'status', 'priority', 'due_date', 'created_at', 'updated_at', 'tags'];
    
    def __init__(self, id: int, name: str, description: str, status: TaskStatus, priority: TaskPriority, due_date: str | None, created_at: str | None, updated_at: str | None, tags: list[str] | str | None):
        if(not isinstance(id, int)):
            raise TaskException("Task id must be an integer");
        if(not isinstance(name, str)):
            raise TaskException("Task name must be a string");
        if(not isinstance(description, str)):
            raise TaskException("Task description must be a string");
        if(not isinstance(status, TaskStatus)):
            try:
                status = tsSet(status.split(".")[1]);
            except Exception as e:
                raise e;
        if(not isinstance(priority, TaskPriority)):
            try:
                priority = tpSet(priority.split(".")[1]);
            except Exception as e:
                raise e;
        if(not isinstance(due_date, str) and due_date is not None):
            raise TaskException("Task due date must be a string or None");
        if(not isinstance(created_at, str) and created_at is not None):
            raise TaskException("Task created date must be a string or None");
        if(not isinstance(updated_at, str) and updated_at is not None):
            raise TaskException("Task updated date must be a string or None");
        
        self.id = id;
        self.name = name;
        self.description = description;
        self.status = status;
        self.priority = priority;
        self.due_date = due_date;
        self.created_at = created_at;
        self.updated_at = updated_at;
        if(isinstance(tags, str)):
            self.tags = tags;
        else:
            self.tags = getTags(tags);
    
    def getTaskStatusString(self) -> str:
        return {
            TaskStatus.PENDING: '- [ ]',
            TaskStatus.IN_PROGRESS: '- [_]',
            TaskStatus.COMPLETED: '- [x]',
            TaskStatus.CANCELED: '- [c]',
            TaskStatus.DELETED: '- [d]'
        }[self.status];
        
    def getTaskPriorityString(self) -> str:
        return {
            TaskPriority.LOW: '(!)',
            TaskPriority.MEDIUM: '(!!)',
            TaskPriority.HIGH: '(!!!)',
            TaskPriority.URGENT: '(_!!!!_)'
        }[self.priority];
    
    def getTaskIdString(self) -> str:
        return f"[id::{self.id}]";
    
    def __str__(self) -> str:
        return f"{self.getTaskStatusString()} {self.getTaskPriorityString()} {self.getTaskIdString()} {self.name} - {self.description} - 📅{self.due_date}";
   
    def __repr__(self) -> str:
        return f"Task(id={self.id}, name={self.name}, description={self.description}, status={self.status}, priority={self.priority}, due_date={self.due_date}, created_at={self.created_at}, updated_at={self.updated_at})";
    
    def __eq__(self, other) -> bool:
        return self.id == other.id;
    
    def __hash__(self) -> int:
        return hash(self.id);
    
    def __dict__(self) -> dict:
        return {
            'id':           int(self.id),
            'name':         self.name,
            'description':  self.description,
            'status':       tsGet(self.status),
            'priority':     tpGet(self.priority),
            'due_date':     self.due_date,
            'created_at':   self.created_at,
            'updated_at':   self.updated_at
        };
        
    def __json__(self) -> str:
        return self.__dict__();
    
    def __tuple__(self) -> namedtuple:
        return namedtuple('Task', ['id', 'name', 'description', 'status', 'priority', 'due_date', 'created_at', 'updated_at'])(self.id, self.name, self.description, self.status, self.priority, self.due_date, self.created_at, self.updated_at);

class FormattedTask(Task):
    """Coerces format into `Task` objects for printing.
    """
    def __init__(self, id: int, name: str, description: str, status: TaskStatus, priority: TaskPriority, due_date: str | None, created_at: str | None, updated_at: str | None, tags: list[str] | None) -> None:
        super().__init__(id, name, description, status, priority, due_date, created_at, updated_at, tags);
        self.set(4, 10, True, True, True);
    
    def getTaskPriorityString(self) -> str:
        priority_str = {
            TaskPriority.LOW: '🔽',
            TaskPriority.MEDIUM: '🔼',
            TaskPriority.HIGH: '⏫',
            TaskPriority.URGENT: '🔺'
        }[self.priority];
        
        return f"{priority_str:<8}";
    
    def set(self, nameWidth: int, descriptionWidth: int, showTags: bool, showCreated: bool, showUpdated: bool) -> None:
        if(not isinstance(nameWidth, int)):
            raise TaskException("Task name width must be an integer");
        if(not isinstance(descriptionWidth, int)):
            raise TaskException("Task description width must be an integer");
        if(not isinstance(showTags, bool)):
            raise TaskException("Task show tags must be a boolean");
        if(not isinstance(showCreated, bool)):
            raise TaskException("Task show created date must be a boolean");
        if(not isinstance(showUpdated, bool)):
            raise TaskException("Task show updated date must be a boolean");
        
        
        self.name = f"{self.name:<{nameWidth}}";
        self.description = f"{self.description:<{descriptionWidth}}";
        self.tags = f"{self.tags}" if showTags else "";
        self.created_at = f"{self.created_at}" if showCreated else "";
        self.updated_at = f"{self.updated_at}" if showUpdated else "";
        
        self.format = {
            'nameWidth': nameWidth,
            'descriptionWidth': descriptionWidth,
            'showTags': showTags,
            'showCreated': showCreated,
            'showUpdated': showUpdated
        };
        
    def __str__(self) -> str:
        catched_str = super().__str__();
        
        if(self.format["showCreated"] == False):
            catched_str = catched_str.replace(f"- cdate::{self.created_at}", "");
        if(self.format["showUpdated"] == False):
            catched_str = catched_str.replace(f"- udate::{self.updated_at}", "");        
        if(self.format['showTags']):
            catched_str += f" - {self.tags}";
        if(self.due_date is None):
            catched_str = catched_str.replace("- due::None", "");
        
        return catched_str;
    
    def __json__(self) -> str:
        return super().__json__() + self.format;
    
    def get(self) -> dict:
        return {
            'format': {
                'nameWidth': self.format['nameWidth'],
                'descriptionWidth': self.format['descriptionWidth'],
                'showTags': self.format['showTags'],
                'showCreated': self.format['showCreated'],
                'showUpdated': self.format['showUpdated']
            },
            
            'task': {
                'id': self.id,
                'name': self.name,
                'description': self.description,
                'status': str(self.status),
                'priority': str(self.priority),
                'due_date': self.due_date,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'tags': self.tags
            }            
        };


def setRandomTask() -> FormattedTask:
    from math import floor;
    from random import choice, random;
    from string import ascii_letters;
    from datetime import datetime;
    
    id = floor(1000 + (9999 - 1000) * random());
    name = ''.join(choice(ascii_letters) for i in range(10));
    description = ''.join(choice(ascii_letters) for i in range(50));
    status = choice(list(TaskStatus));
    priority = choice(list(TaskPriority));
    due_date = "2024-04-28";
    created_at = "2024-04-28";
    updated_at = "2024-04-28";
    
    return FormattedTask(id, name, description, status, priority, due_date, created_at, updated_at, None);

def setTaskFromDict(task: dict) -> Task:
    return Task(task['id'], task['name'], task['description'], task['status'], task['priority'], task['due_date'], task['created_at'], task['updated_at'], task['tags']);

def setFormattedTaskFromDict(task: dict) -> FormattedTask:
    return FormattedTask(task['task']['id'], task['task']['name'], task['task']['description'], task['task']['status'], task['task']['priority'], task['task']['due_date'], task['task']['created_at'], task['task']['updated_at'], task['task']['tags']);

#   Parser classes for Task objects
#   -------------------------------------------------------------------------------------------------------------------
class TaskParser:
    __slots__ = ['options']
    
    TP__DEFAULT_OPTIONS_DICT:dict={
        'verbose': False,
        'zettelkasten': False
    };
    
    
    TP__VERBOSE_INPUT_MESSAGE:str="""
    A `Task` object is composed of the following attributes:
    - id            : unique identifier for the task
    - name          : name of the task
    - description   : description of the task
    - status        : status of the task
    - priority      : priority of the task
    - due_date      : due date of the task
    
    Insert each field to create a new `Task` object.
    ----------------------------------------------------------
    
    """;
    
    TP__DEFAULT_INPUT_MESSAGE:str="""
    Insert each field to create a new `Task` object.
    ----------------------------------------------------------
    
    """;
    
    TP__DEFAULT_INPUT_FIELD:str=" >  ";
    
    
    
    def __init__(self, options:dict=TP__DEFAULT_OPTIONS_DICT) -> None:
        self.options = options;
    
    def _getUserInput(self) -> str:
        if(self.options['verbose']):
            return input(self.TP__VERBOSE_INPUT_MESSAGE);
        return input(self.TP__DEFAULT_INPUT_MESSAGE);
    
    def parse(self, id:int) -> FormattedTask:        
        try:
            name            = input(self.TP__DEFAULT_INPUT_FIELD + "name: ");
            description     = input(self.TP__DEFAULT_INPUT_FIELD + "description: ");
            status          = TaskStatus[input(self.TP__DEFAULT_INPUT_FIELD + "status: ")];
            priority        = TaskPriority[input(self.TP__DEFAULT_INPUT_FIELD + "priority: ")];
            due_date        = input(self.TP__DEFAULT_INPUT_FIELD + "due_date: ");
            created_at      = datetime.now().strftime('%Y-%m-%d');
            updated_at      = datetime.now().strftime('%Y-%m-%d');
            tags            = input(self.TP__DEFAULT_INPUT_FIELD + "tags: ").split(" ");
            
            ft = FormattedTask(id, name, description, status, priority, due_date, created_at, updated_at, tags);
            print(ft);
            
        except Exception as e:
            print(f"Error: {e}");
            raise e;
        return ft;
        
        
        
        
        
        
        


if __name__ == '__main__':
    print(setRandomTask().get());