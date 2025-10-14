from taskmanager.data_handler import DataHandler
from taskmanager.task_assigner import TaskAssigner
from taskmanager.task_updater import TaskUpdater
from taskmanager.task_clearer import TaskClearer
from taskmanager.ui_controller import UIController

def main():
    try:
        data_handler = DataHandler(filename="task_base.json")
        task_assigner = TaskAssigner(data_handler=data_handler)
        task_updater = TaskUpdater(data_handler=data_handler)
        task_clearer = TaskClearer(data_handler=data_handler,task_updater=task_updater)

        ui_controller = UIController(data_handler, task_assigner, task_updater, task_clearer)

        ui_controller.control_unit()

    except Exception as e:
        print(f"Error starting application: {e}")

if __name__=="__main__":
    main()

'''
* add UI.s

* bug in the update task feature:
    if we update a task to completed mistakenly, it can't be redid as PENDING.
* update the update task part:
    asking for dates before updating the task.
    should automatically label task as UNCOMPLETED or FAILED if the day of the task passed.

* if the user mistakenly chooses an option there is no coming back, try to take an input q that returns back to the menu. 
'''