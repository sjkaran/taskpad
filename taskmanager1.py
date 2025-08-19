import os
from datetime import date, datetime, timedelta
import json

class taskmanager2:
    def __init__(self,filename="task2.json"):
        self.filename = filename
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.filename):
            initial_data= {"tasks":{}}
            with open (self.filename,"w")as file:
                json.dump(initial_data,file,indent=4)
                
    @staticmethod
    def display_data(data):
        if len(data["tasks"])>0:
            for dates in data["tasks"]:
                print(f"\nDate: {dates}")
                for n in data["tasks"][dates]:
                    num = data["tasks"][dates][n]
                    print(f"{n}. {num["task"]}\t[{num["result"]}]\n   remark: {num["remark"]}")

    @staticmethod
    def view_data(displays: bool):
        # provides the loaded data with running the display data.
        with open("task2.json","r")as f:
            loaded_data =json.load(f)
        if displays:
            taskmanager2.display_data(loaded_data)
        else:
            return loaded_data

    @staticmethod
    def upload_data(newdata):
        with open("task2.json","w")as file:
            json.dump(newdata,file,indent=4)

    @staticmethod
    def indexof(funcName):
        # determines the index for various functions like updating, asigning and clearing tasks.
        def take_input(ref):
            hir = ["date","num","task"]   #can add more attributes to the dict format later.
            user =[]
            try:
                for i in range(hir.index(ref)):
                    user.append(input(f"enter the {hir[i]} of the task you want to {funcName}."))
            except ValueError:
                print("try again.")
                take_input(ref)
            except Exception as e:
                print("unexpected error detected: ")
                take_input(ref)
            return user
        if funcName=="update":
            indexis = take_input("task")
            return indexis
        elif funcName=="assign":
            indexis = take_input("num")
            return indexis
        elif funcName=="clear":
            indexis=take_input("task")
            return indexis

    @staticmethod
    def update_task(data):
        # updates the existing tasks.
        index = taskmanager2.indexof("update")
        while True:
            try:
                yn= input("is the task completed: ")
                if yn.lower().startswith('y'):
                    data["tasks"][index[0]][index[1]]["result"]="Completed"
                    print("good job.... \ntask updated.")
                elif yn.lower().startswith('n'):
                     data["tasks"][index[0]][index[1]]["remark"]= input("what is you remark for it.")
                else:
                    raise KeyboardInterrupt("couldn't get your input.")
            except KeyboardInterrupt:
                print('trying again.')
            except Exception as e:
                print("error detected.")
            else:
                break

        taskmanager2.upload_data(data)
    
    @staticmethod
    def assign_task(data):
        # assigns the new tasks.
        today = str(date.today())
        tomorrow = str(date.today()+timedelta(days=1))
        def assigning(data,date_str,n):
                try:
                    if date_str not in data["tasks"]:
                        data["tasks"][date_str]={}
                    for i in range(1,n+1):
                        data["tasks"][date_str][str(i)]={
                            'task':input(f"enter the no.{i} task for {date_str}. \n\t:"),
                            'result': 'pending',
                            'remark': 'pending'
                            }
                    return True
                except Exception as e:
                    print("try again error occured.")
                    return False
        while True:
            try:
                numOfTasks = int(input("enter the number of tasks you want to assign:"))
                if numOfTasks>0 and numOfTasks<10:
                    userDate = input("do you want to assign them in today?")
                    if userDate.lower().startswith('y'):
                        if assigning(data,today,numOfTasks):
                            taskmanager2.upload_data(data)
                            break
                        
                    elif userDate.lower().startswith('n'):
                        if assigning(data, tomorrow,numOfTasks):
                            taskmanager2.upload_data(data)
                            break
                    else:
                        print("couldn't get your input.")
                else:
                    print("task should be in between 1-9 in quantity.")
            except ValueError:
                print("trying again")
            except Exception as e:
                print("error occured:",e)
                break


    @staticmethod
    def clear_task(data):
        # clears the outdated tasks.
        try:
            idx = taskmanager2.indexof("clear")
            del data["tasks"][idx[0]][idx[1]]
            print("task cleared successfully.")
        except Exception as e:
            print("error detected in clearing task.")

    def control_unit(self):
        # governs the total systems by taking input from the user.
        try:
            while True:
                loaded_data = taskmanager2.view_data(False)
                print("Chose one: \n1.view Tasks\n2. Assign tasks\n3. Update Tasks.\n4.Clear tasks.\n5. Nothing")
                inp = int(input("\t::>"))
                if inp==1:
                    taskmanager2.view_data(True)
                elif inp==2:
                    taskmanager2.assign_task(loaded_data)
                elif inp==3:
                    # taskmanager2.update_task(loaded_data)
                    print("works going on, we will be in service soon.")
                elif inp==4:
                    # taskmanager2.clear_task(loaded_data)
                    print("works going on, we will be in service soon.")
                elif inp==5:
                    print("have a productive day sir.")
                    break
                else:
                    print("type in 1-5")
        except ValueError:
            print("please enter a number between 1-5.")
        except Exception as e:
            print("error occured. try again.")

# checks if the file exists and creates and initiates the file with the initial format.
if not os.path.exists("task2.json"):
    with open("task2.json","w")as f:
        json.dump({"tasks":{}},f)

if __name__=="__main__":
    taskmanager = taskmanager2()
    taskmanager.control_unit()