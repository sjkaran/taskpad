import os
from datetime import datetime, timedelta
import json

class taskmanager2:
    def __init__(self,filename="task2.json"):
        self.filename = filename
        self.ensure_file_exists()

    def ensure_file_exists(self):
        initial_data = {"tasks":{}}

        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump(initial_data,f,indent=4)
            return
        
        try:
            with open(self.filename,"r+")as f:
                try:
                    loaded_data = json.load(f)
                except json.JSONDecodeError:
                    loaded_data= None

                if not loaded_data:
                    f.seek(0)
                    f.truncate()
                    json.dump(initial_data,f,indent=4)
        except FileNotFoundError:
            with open(self.filename,"w")as f:
                json.dump(initial_data,f,indent=4)

                
    def display_data(self,data):
        # display task data in formatted output 
        if len(data["tasks"])>0:
            for dates in data["tasks"]:
                print(f"\nDate: {dates}")
                for n in data["tasks"][dates]:
                    num = data["tasks"][dates][n]
                    print(f"{n}. {num["task"]}\t[{num["result"]}]\n   remark: {num["remark"]}")
        else:
            print("\nNo task found. Start by assigning some tasks!")

    def view_data(self,displays: bool):
        # loads data from file and optionally displays it.
        try:
            with open(self.filename,"r")as f:
                loaded_data = json.load(f)
            if displays:
                self.display_data(loaded_data)
            return loaded_data
        except FileNotFoundError:
            print(f"Error File {self.filename} not found.")
            return {"tasks":{}}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.filename}")
            return {"tasks":{}}
        
    def upload_data(self, newdata):
        #save data to file with error handling.
        try:
            with open(self.filename, "w")as file:
                json.dump(newdata,file,indent=4)
            return True
        except Exception as e:
            print(f"Error in saving data: {e}")
            return False

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
        
        data = self.view_data(False)

        #show current tasks first
        print("\nCurrent tasks:")
        self.display_data(data)

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
                    yn = input("\nIs the task completed (y/n)").strip()
                    if yn.lower().startswith('y'):
                        data['tasks'][date_key][task_num]['result'] = "COMPLETED 🎯"
                        print("Good job! Task marked as completed.")
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
                
            if self.upload_data(data):
                print(f"Task updated successfully!")
            else:
                print("Error saving udated task.")

        except Exception as e:
            print(f"Error updating task : {e}")
        
    
    
    def assign_task(self):
        # assing new tasks with proper data key initialization.

        data = self.view_data(False)
        today = datetime.now().strftime("Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        def assigning(data,date_str,n):
                """Inner fuction to handle task assignment"""
                try:
                    if date_str not in data["tasks"]:
                        data["tasks"][date_str]={}

                    print(f"\nAssigning {n} tasks for {date_str}:")
                    for i in range(1,n+1):
                        task_input = input(f"Enter task - {i}:").strip()
                        if not task_input:
                            return False
                        
                        data["tasks"][date_str][str(i)]={
                            'task': task_input,
                            'result':'pending',
                            'remark':'pending'
                        }
                        return True
                except Exception as e:
                    print(f"Error occured during assignment: {e}")
                    return False
        try:
            while True:
                try:
                    numOfTasks = int(input("Enter the number of tasks you want to assign: "))
                    if numOfTasks <= 0 or numOfTasks >=10:
                        print("Please enter a number between 1 and 9.")
                        continue

                    userDate = input("Do you want to assign your tasks for today?   ").strip()

                    if userDate.lower().startswith('y'):
                        if assigning(data, today, numOfTasks):
                            if self.upload_data(data):
                                print(f"✅ {numOfTasks} tasks assigned for today ({today})")
                            else:
                                print("Error saving tasks.")
                            break
                    elif userDate.lower().startswith('n'):
                        if assigning(data, tomorrow, numOfTasks):
                            if self.upload_data(data):
                                print(f"✅ {numOfTasks} tasks assigned for tomorrow ({tomorrow})")
                            else:
                                print("Error saving tasks.")
                            break
                    else:
                        print("Please try to enter 'yes' or 'no' for tomorrow.")

                except ValueError:
                    print("Please enter a valid number.")
                except KeyboardInterrupt:
                    print("\nOperation Cancelled.")
                    break
                except Exception as e:
                    print(f"Error occured: {e}")
                    break

        except Exception as e:
            print(f"Error in tasks assignment: {e}")


    def clear_task(self):
        # Clear/delete existing tasks with fresh data loading.

        data = self.view_data(False)

        print("\nCurrent tasks: ")
        self.display_data(data)
        
        if len(data["tasks"])==0:
            print("No tasks to clear!")
            return
        
        try:
            idx = self.indexof("clear")
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
                
                if self.upload_data(data):
                    print("✅ Task cleared successfully!")
                else:
                    print("Error saving changes.")
            else:
                print("Task deletion cancelled.")

        except KeyError as e:
            print(f"Task not found: {e}")
        except Exception as e:
            print(f"Error detection in clearing tasks: {e}")


    def view_option(self):
        print("\n"+"-"*30)
        print("Choose an option:")
        print("1. View Tasks")
        print("2. Assign Tasks")
        print("3. Update Tasks")
        print("4. Clear Tasks")
        print("5. Exit")
        print("-"*30)



    def control_unit(self):
        """ Main control interface with the fresh data loading per operation """
        print("-"*50)
        print(" TASK MANAGER ")
        print("-"*50)

        try:
            while True:
                self.view_option()
                try:
                    inp= input("Enter your choice :").strip().lower()
                    match inp:
                        case str() if inp =='1' or inp.startswith('v'):
                            print("\n📃 CURRENT TASKS: ")
                            self.view_data(True)

                        case str() if inp == '2' or inp.startswith('as'):
                            print("\n➕ ASSIGNING NEW TASKS:")
                            self.assign_task()

                        case str() if inp =='3' or inp.startswith('up'):
                            print("\n◴ UPDATE TASKS:")
                            self.update_task()

                        case str() if inp=='4' or inp.startswith('cl'):
                            print("\n🧹 CLEAR TASKS:")
                            self.clear_task()
                        
                        case str() if inp=='5' or inp.startswith('ex'):
                            print("\n🙏 Have a productve day! 🎯")
                            break

                        case _:
                            print("Please enter a number between 1 to 5 or else type the choice correctly.")
                except ValueError:
                    print("⚠️ Please enter a valid input.")
                
                except KeyboardInterrupt:
                    print("\n\n Goodbye! 🙋‍♂️")
                    break
        except Exception as e:
            print(f"Unexpected error in control unit: {e}")

if not os.path.exists("task2.json"):
    with open("task2.json","w") as f:
        json.dump({"tasks": {}},f)

if __name__=="__main__":
    try:
        taskmanager2 = taskmanager2()
        taskmanager2.control_unit()

    except Exception as e:
        print(f"Error starting application: {e}")
