from taskmanager import *
class TaskClearer:
    def __init__(self,data_handler,task_updater):
        self.data_handler = data_handler
        self.task_updater = task_updater

    def date_wize_cleaner(self):
        pass

    def remark_wize_cleaner(self):
        pass

    def manual_cleaner(self):
        pass

    def clean_ui_controler(self):
        def options():
            print("How you wanna remove the tasks: ")
            print("1. remove out dated tasks.")
            print("2. remove completed tasks.")
            print("3. remove tasks manually.")
            print("4. go back to menu.")
            try:
                inp = input("")
                return inp
            except Exception as e:
                print(f"{e}\nloc: {__class__.__name__}\{options.__name__}")

        def final_clean_ui():            
            while True:
                try:
                    ipt = options()
                    match ipt:
                        case m if m in ('1','rm out','remove out dated','out'):
                            print("activate date wize cleaner.")
                        case m if m in ('2','rm comp','completed','complete'):
                            print("activate date wize cleaner.")
                        case m if m in ('3','remove manualy','manualy','rm man'):
                            print("activate the manual cleaner:")
                        case m if m in ('4','menu','go','back'):
                            break
                except KeyboardInterrupt:
                    print("Operation canceled by the user. (key board inturupt error)")
                    break
                except EOFError:
                    print("\nInput stream closed (EOFError). Exititng ")
                    break
                except Exception as e:
                    print(f"Error occured {e}\nloc: {__class__.__name__}/{self.clean_ui_controler.__name__}")
                    break
        
        self.data = self.data_handler.view_data(False)
        if len(self.data["tasks"])<=0:
            print("- "*10,end="-")
            print("Assign the task first",end="-")
            print("- "*10,end="-")
        else:
            self.data_handler.display_data(self.data)
            final_clean_ui()


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
