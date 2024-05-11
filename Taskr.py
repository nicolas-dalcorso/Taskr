"""
Stand-alone module for managing tasks.

nrdc
2024-04-29
v0.1.0
"""

from enum                   import Enum;
from typing                 import List, Any;
from datetime               import datetime;
from time                   import time;
from modules.jsonShelves    import *;
from modules.tasks          import *;
from modules.loggr          import *;
from modules.hashr          import Hashr;
from modules.textWrappers   import *;


#   Status codes for the `Taskr` class.
class TaskrStatus(Enum):
    TASKR_STATUS__SUCCESS           = 0;
    TASKR_STATUS__ERR_FILE_NOT_FOUND= 1;
    TASKR_STATUS__ERR_CANNOT_WRITE  = 2;
    TASKR_STATUS__ERR_UNKNOWN       = 3;
    TASKR_STATUS__ERR_PARSER        = 4;
    TASKR_STATUS__ERR_TASK          = 5;
    TASKR_STATUS__ERR_FORMATTEDTASK = 6;
    TASKR_STATUS__ERR_LOGGR         = 7;

#   Sub-class of the `jsonShelves` `IterableShelve` class for creating, storing, retrieving, editing and removing `FormattedTask` objects
class TaskShelf(IterableShelve):
    def __init__(self, filepath:str) -> None:
        super().__init__(filepath);
        
    def search(self, task_id:int) -> FormattedTask | None:
        for task in self.data:
            if(task['id'] == task_id):
                return setFormattedTaskFromDict(task);
        return None;
        
    
    def insert(self, task:FormattedTask) -> TaskrStatus:
        """Inserts a new `FormattedTask` to the `TaskShelf` object.
        If the task already exists, it will be updated. If the task does not exist, it will be added.
        A task is considered to exist if the `id` attribute of the `FormattedTask` object is already present in the `TaskShelf` object.

        Returns:
            TaskrStatus.TASKR_STATUS__SUCCESS if the task was successfully inserted.
            TaskrStatus.TASKR_STATUS__ERR_TASK if the task could not be inserted.
        """
        try:
            self.data.append(task.get());
            return TaskrStatus.TASKR_STATUS__SUCCESS;
        except Exception as e:
            print(e);
            return TaskrStatus.TASKR_STATUS__ERR_TASK;
    
    def remove(self, task_id:int) -> TaskrStatus:
        """Removes a `FormattedTask` from the `TaskShelf` object given its `id` attribute.

        Returns:
            TaskrStatus.TASKR_STATUS__SUCCESS if the task was successfully removed.
            TaskrStatus.TASKR_STATUS__ERR_TASK if the task could not be removed.
        """
        for index, ftask in enumerate(self.data):
            if(ftask['id'] == task_id):
                del self.data[index];
                return TaskrStatus.TASKR_STATUS__SUCCESS;
        return TaskrStatus.TASKR_STATUS__ERR_TASK;
    
    def update(self, task:FormattedTask) -> TaskrStatus:
        """Updates a `FormattedTask` in the `TaskShelf` object given its `id` attribute.

        Returns:
            TaskrStatus.TASKR_STATUS__SUCCESS if the task was successfully updated.
            TaskrStatus.TASKR_STATUS__ERR_TASK if the task could not be updated.
        """
        for index, ftask in enumerate(self.data):
            if(ftask['id'] == task.get()['id']):
                self.data[index] = task.get();
                return TaskrStatus.TASKR_STATUS__SUCCESS;
        return TaskrStatus.TASKR_STATUS__ERR_TASK;
    
    def get(self, task_id:int) -> FormattedTask | None:
        for task in self.data:
            if(task['id'] == task_id):
                return setFormattedTaskFromDict(task);
        return None;
    
    def get(self) -> List[FormattedTask]:
        return [setFormattedTaskFromDict(task) for task in self.data];

    
    def close(self) -> TaskrStatus:
        try:
            self.save();
            return TaskrStatus.TASKR_STATUS__SUCCESS;
        except:
            return TaskrStatus.TASKR_STATUS__ERR_CANNOT_WRITE;
    


#   The `TaskFile` namedtuple contains information about the tasks file.
TaskFileData = namedtuple('TaskFileData', ['filepath', 'num_tasks', 'size', 'created', 'last_acessed', 'sha256']);


    

class Taskr:
    """Manager class for `Task`, `FormattedTask` objects.
    """
    __slots__ = ['parser', 'shelve', 'loggr'];
    parser: TaskParser | None;
    shelve: TaskShelf | None;
    loggr: Loggr | None;
    
    DEFAULT__FILEPATH_DICT = {
        'logfile'           : r'./logs/taskr.log',
        'tasks_dict'        : r'./data/tasks_dict.json',
        'taskfile'          : r'./data/tasks.txt'
    };
    
    DEFAULT__LOGGR_CONFIG = {
        'log_file'          : DEFAULT__FILEPATH_DICT['logfile'],
        'log_level'         : LogLevel.DEBUG,
        'formatter_string'  : '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'datefmt'           : '%m-%d-%Y %I:%M:%S %p'
    };
    
    def __checkFiles(self, filepaths:dict, create_always:bool=False) -> bool:
        """Check if each file in the `filepaths` dictionary exists. Creates the file if it does not exist.
        If the `create_always` flag is set to `True`, the file will be created regardless of its existence.
        """
        #   Check if files exist
        for key in filepaths:
            if(not os.path.exists(filepaths[key])):
                try:
                    with open(filepaths[key], 'w') as f:
                        f.write('');
                except:
                    return False;
            else:
                if(create_always):
                    try:
                        with open(filepaths[key], 'w') as f:
                            f.write('');
                    except:
                        return False;
    
    def __init__(self, filepaths:dict=DEFAULT__FILEPATH_DICT, loggr_config:dict=DEFAULT__LOGGR_CONFIG):
        self.__checkFiles(filepaths);
        
        self.parser = TaskParser();
        self.shelve = TaskShelf(filepaths['tasks_dict']);
        self.loggr  = Loggr(loggr_config['log_file'], loggr_config['log_level'], loggr_config['formatter_string'], loggr_config['datefmt']);
        
        self.loggr.info('Taskr initialized.');
 
    def __len__(self) -> int:
        return len(self.tasks);
    
    def size(self) -> int:
        return os.path.getsize(self.shelve.filepath);
    
    def getTaskFileData(self) -> TaskFileData:
        filepath    = self.shelve.filepath;
        num_tasks   = len(self.shelve.data);
        size        = self.size();
        created     = datetime.fromtimestamp(os.path.getctime(filepath));
        last_acessed= datetime.fromtimestamp(os.path.getatime(filepath));
        hash_sha256 = Hashr().hash_file(file_path=filepath);
        
        return TaskFileData(filepath, num_tasks, size, created, last_acessed, hash_sha256);
         
    def update(self):
        self.shelve.save();
        self.loggr.info('Taskr updated.');
    
    def count(self) -> int:
        return len(self.tasks);
     
    def close(self):
        self.shelve.save();
        self.loggr.info('Taskr closed.');

    def newTask(self) -> TaskrStatus:
        """Creates a new task from user input and adds it to the `Taskr` object.

        Returns:
            TaskrStatus.TASKR_STATUS__SUCCESS if the task was successfully created.
            TaskrStatus.TASKR_STATUS__ERR_TASK if the task could not be created.
        """
        #   Get a unique identifier for the task
        try:
            task_id = self.shelve.data[-1]['task']['id'] + 1;
        except:
            task_id = 0;
        
        #   Get the task from the user
        task = self.parser.parse(task_id);
        
        #   Insert the task into the `Taskr` object
        if(self.shelve.insert(task) == True):
            self.loggr.info(f"Task {task_id} added.");
            return TaskrStatus.TASKR_STATUS__SUCCESS;
        else:
            self.loggr.error(f"Task {task_id} could not be added.");
            return TaskrStatus.TASKR_STATUS__ERR_TASK;

    def view(self) -> TaskStatus:
        """Prints all the tasks in the `Taskr` object.

        Returns:
            TaskStatus.TASK_STATUS__SUCCESS if the tasks were successfully printed.
            TaskStatus.TASK_STATUS__ERR_TASK if the tasks could not be printed.
        """
        for task in self.shelve.data:
            print(" >  ", setFormattedTaskFromDict(task), sep="");
        return TaskrStatus.TASKR_STATUS__SUCCESS;
    
    def generateTaskFile(self) -> TaskStatus:
        try:
            with open('./data/tasks.md', 'w', encoding="utf-8") as f:                
                f.write(f"# Lista de Tarefas [{datetime.now().strftime('%d-%m-%y %H:%M:%S')}]\n\n");
                
                for task in self.shelve.data:
                    f.write(f"{setFormattedTaskFromDict(task)}\n");                    
                
                f.write("\n\n---\n");
            return TaskrStatus.TASKR_STATUS__SUCCESS;
        except Exception as e:
            self.loggr.error(f"An Error occurredTasks could not be generated in '.md' format.");



class Main:
    """Main class for running the `Taskr` program
    """
    DEFAULT_MESSAGES:dict[str,str] = {
        "INPUT"             : " >  ",
        "SEPARATOR"         : "="*64,
        "PRESENTATION"      : "\t\tTASKR v1.0.\n\n\t\tnrdc\n\t\t2024",
        "DESCRIPTION"       : 
"""
\t - `new task`       :: includes a new task
\t - `edit task`      :: given an id, updates a task
\t - `remove task`    :: given an id, removes a task
\t - `view`           :: lists all the tasks
\t - `quit` || `q`    :: exits the program
\t - `generate`       :: generates the tasks file in '.md' format
"""
    };
    
    
    def __init__(self) -> None:
        self.history:list[str]  = [];
        self.taskr              = Taskr();
    
        #   Prints to stdout the presentation for the program
        self.intro();
        
        #   Runs the program
        self.main();
        
    
    def intro(self) -> None:
        print(self.DEFAULT_MESSAGES["SEPARATOR"], self.DEFAULT_MESSAGES["PRESENTATION"], self.DEFAULT_MESSAGES["SEPARATOR"], self.DEFAULT_MESSAGES["DESCRIPTION"], self.DEFAULT_MESSAGES["SEPARATOR"],
              sep="\n",
              end="\n\n");
        
    def main(self) -> None:
        #   Defines a dictionary for storing session data
        data:dict[str, Any]={
            "session_start" : datetime.now().strftime("%d-%m-%y %H:%M:%S"),
            "time_start"    : time(),
            "call_count"    : 0
        };
        
        #   Flag for the while loop        
        running:bool = True;
        
        while(running):
            #   Increment the call count
            data["call_count"] += 1;
            
            #   Get the user input
            if(running):
                usr_input = self.listen();
            
            #   Process the user input
            if(usr_input == "new task"):
                
                if(self.taskr.newTask() == TaskrStatus.TASKR_STATUS__SUCCESS):
                    self.history.append(usr_input);
                    self.taskr.loggr.debug(f"New task added.");
                    self.taskr.update();
                
            elif(usr_input == "edit task"):
                pass;
            elif(usr_input == "remove task"):
                pass;
            elif(usr_input == "view"):
                if(self.taskr.view() == TaskrStatus.TASKR_STATUS__SUCCESS):
                    self.history.append(usr_input);
                    self.taskr.loggr.debug(f"Tasks viewed.");
                    
            elif(usr_input == "quit" or usr_input == "q"):
                self.taskr.close();
                running = False;
                
            elif(usr_input == "generate"):
                self.history.append(usr_input);
                if(self.taskr.generateTaskFile() == TaskrStatus.TASKR_STATUS__SUCCESS):
                    self.taskr.loggr.debug(f"Tasks generated in '.md' format at {datetime.now().strftime('%d-%m-%y %H:%M:%S')} (file::`tasks.md`)");
                else:
                    self.taskr.loggr.error(f"Tasks could not be generated.");
                
            else:
                print("Invalid command.");
            
      
    def listen(self) -> str:
        try:
            usr_input = input(self.DEFAULT_MESSAGES["INPUT"]);
        except EOFError:
            usr_input = "";
        finally:
            return usr_input;
        
        
        
def meanTaskSize(taskr:Taskr)->str:
    """Calculates the mean size of a task in the `Taskr` object.

    Args:
        taskr (Taskr): The `Taskr` object to calculate the mean task size for.

    Returns:
        str: A string representation of the mean task size.
    """
    def strBytes(nbytes:int)->str:
        """Transforms a quantity of bytes in a natural language string using the common units of measure for bytes.

        Args:
            s (_type_): _description_
        """
        if(nbytes < 1024):
            return f"{nbytes} bytes";
        elif(nbytes < 1048576):
            return f"{nbytes / 1024} KB";
        elif(nbytes < 1073741824):
            return f"{nbytes / 1048576} MB";
        else:
            return f"{nbytes / 1073741824} GB";
    
    print("size: ", strBytes(taskr.size()))
    return strBytes(taskr.size() / taskr.getTaskFileData().num_tasks);   
    
if __name__ == '__main__':
    main = Main().main();


