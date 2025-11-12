from taskmanager.data_handler import DataHandler
from taskmanager.task_assigner import TaskAssigner
from taskmanager.task_updater import TaskUpdater
from taskmanager.task_clearer import TaskClearer
from taskmanager.ui_controller import UIController
from taskmanager.task_viewer import TaskViewer

def main():
    try:
        data_handler = DataHandler(filename="task_base.json")
        task_assigner = TaskAssigner(data_handler=data_handler)
        task_updater = TaskUpdater(data_handler=data_handler)
        task_clearer = TaskClearer(data_handler=data_handler)
        task_viewer = TaskViewer(DataHandler=data_handler)

        ui_controller = UIController(data_handler, task_assigner, task_updater, task_clearer,task_viewer=task_viewer)

        ui_controller.control_unit()

    except Exception as e:
        print(f"Error starting application: {e}")

if __name__=="__main__":
    main()

'''
* add UI.s

* bug in the update task feature. (if you entered to choose yesterday's task mistakenly then it's showing error.)

* the interface should show all the pending tasks in the time of running the interface. then ask for choice.

* tasks should be automatically set to failed or should ask the user to determine a postponed date for the task one by one or else tasks should marked as faild.
* failed task must stored in another file along with passed tasks to determine the pattern of success for future ai use.

'''