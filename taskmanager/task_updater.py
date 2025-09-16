class TaskUpdater:
    def __init__(self,data_handler):
        self.data_handler = data_handler
    
    def indexof(self, funcName):
       # get index inputs for various operation with improved validation.
        def take_input(ref):
            hir = ["date","num","task"]
            user =[]
            try:
                for i in range(hir.index(ref)):
                    prompt = f"Enter the {hir[i]} of the task you want to {funcName}: "
                    user_input = input(prompt).strip()
                    if not user_input:
                        print("Input cannot be empty. Please try again.")
                        return take_input(ref)
                    user.append(user_input)
            except ValueError:
                print("Invalid reference. Please try again.")
                return take_input(ref)
            except Exception as e:
                print(f"Unexpected error detected : {e}")
                return take_input(ref)
            return user
        
        if funcName == "update":
            return take_input("task")
        elif funcName == "assign":
            return take_input("num")
        elif funcName == "clear":
            return take_input("task")

    def update_task(self):
        # update existing tasks with fresh data loading.
        
        data = self.data_handler.view_data(False)

        #show current tasks first
        print("\nCurrent tasks:")
        print("-"*30)
        self.data_handler.display_data(data)

        if len(data["tasks"]) ==0:
            print("No tasks to update!")
            return
        
        try:
            index = self.indexof("update")
            date_key = index[0]
            task_num = index[1]


            if date_key not in data["tasks"]:
                print(f"No tasks found for date: {date_key}")
                return
            
            if task_num not in data["tasks"][date_key]:
                print(f"Task number {task_num} not found for date {date_key}")
                return
            

            current_task = data["tasks"][date_key][task_num]
            print(f"\nCurrent task: {current_task['task']}")
            print(f"Status: {current_task['result']}")
            print(f"Remark: {current_task['remark']}")

            while True:
                try:
                    yn = input("\nIs the task completed (y/n): ").strip()
                    if yn.lower().startswith('y'):
                        data['tasks'][date_key][task_num]['result'] = "COMPLETED"
                        print("Task marked as completed.")
                        break
                    elif yn.lower().startswith('n'):
                        new_remark = input("What is your remark for it: ").strip()
                        data["tasks"][date_key][task_num]["remark"]=new_remark
                        print("Task remark updated.")
                        break
                    else:
                        print("Please answer on Yes or No ")
                except KeyboardInterrupt:
                    print("\nOperation cancelled.")
                    return
                except Exception as e:
                    print(f"Error occured: {e}")
                    return
                
            if self.data_handler.upload_data(data):
                print(f"Task updated successfully!")
            else:
                print("Error saving udated task.")

        except Exception as e:
            print(f"Error updating task : {e}")


'''
* shorten up the indexof function.
* enable auto update to outdated function.
'''