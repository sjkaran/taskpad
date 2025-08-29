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