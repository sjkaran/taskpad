class TaskClearer:
    def __init__(self,data_handler,task_updater):
        self.data_handler = data_handler
        self.task_updater = task_updater

    def clear_task(self):
        # Clear/delete existing tasks with fresh data loading.

        data = self.data_handler.view_data(False)

        print("\nCurrent tasks: ")
        self.data_handler.display_data(data)
        
        if len(data["tasks"])==0:
            print("No tasks to clear!")
            return
        
        try:
            idx = self.task_updater.indexof("clear")
            date_key = idx[0]
            task_num = idx[1]

            if date_key not in data["tasks"]:
                print(f"No tasks found for date: {date_key}")
                return
            
            if task_num not in data["tasks"][date_key]:
                print(f"Task number {task_num} not found for date {date_key}.")
                return 
            
            task_to_delete = data["tasks"][date_key][task_num]
            print(f"\nTask to delete: {task_to_delete['task']}")

            confirm = input("Are you sure you want to delete this task?  :").strip()
            if confirm.lower().startswith('y'):
                del data['tasks'][date_key][task_num]

                if not data['tasks'][date_key]:
                    del data['tasks'][date_key]
                
                if self.data_handler.upload_data(data):
                    print("✅ Task cleared successfully!")
                else:
                    print("Error saving changes.")
            else:
                print("Task deletion cancelled.")

        except KeyError as e:
            print(f"Task not found: {e}")
        except Exception as e:
            print(f"Error detection in clearing tasks: {e}")

    # def remover(self):
    #     pass
    
    # def remove_out_dated(self):
    #     pass

    # def remove_by_completed(self):
    #     pass

    # def manual_remove(self):
    #     pass

    # def ui(self):
    #     pass