from datetime import datetime , timedelta
import re
class TaskUpdater:

    def __init__(self,data_handler):
        self.data_handler = data_handler

    def update_date(self):    #provides the final date
        tries = 0
        while True:
            try:
                indate = input("want to update today's task or yesterday's?\n").lower()
                if 'q'==indate:
                    return "q"
                elif "tod" in indate or "today"==indate or '1'==indate:
                    final_date = datetime.now().strftime("%Y-%m-%d")
                    return final_date
                elif "yes" in indate or "yesterday"==indate or '2'==indate:
                    final_date = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
                    return final_date
                else:
                    if tries==3:
                        print("sorry you tried 3 times but couldn't enterd 1 or 2 atleast.\nTry Later.")
                        return "q"
                    print("your input isn't valid. \n(Enter 1 for today and 2 for yesterday)")
                    tries+=1
            except KeyboardInterrupt:
                print("Time out...!")
                return "q"
            except Exception as e:
                print(f"{e}\noccured try again.")
                return "q"
            
    def view_tasks_to_update(self,data,update_date):       # views the tasks of the entered date to update.
        self.taskCount = 0
        if self.data_handler.check_data():
            if len(data["tasks"][update_date])==0:
                print("NO tasks to update in your choosen day.")
                return False
            else:
                for n in data["tasks"][update_date]:
                    num = data["tasks"][update_date][n]
                    print(f"{n}. {num['task']}\n   result: {num['status']}\n   remark: {num['remark']}")
                    self.taskCount+=1
                return True
                
    def overwrite_task(self,tno,st,rm=' '): #takes the task number and the paramenter to overwrite.
        self.data['tasks'][self.updating_date][tno]['status']=st
        self.data['tasks'][self.updating_date][tno]['remark']=rm
        self.data_handler.upload_data(self.data)
        print(f"task no {tno} updated successfully")
                
    def parameter_of_task(self):#find out which task to update and what to update in that perticular task
        pattern = r'^(\d)/(com\w*|incom\w*|notc\w*|pending|post\w*|trans\w*|fail\w*|done|succe\w*)/(.*)$'
        print("enter your command to update the task among these:\ncommand format: serial_no_of_the_task/status/remark.")
        def parsing():
                try:
                    user = input("\t: ").lower()
                    if user == 'q':         #can cut this off to connect the process directly.
                        return 'q'
                    else:
                        match = re.match(pattern, user)
                        if match:
                            slno = match.group(1)
                            status = match.group(2)
                            remark = match.group(3) if match.group(3) else " "
                            return [slno,status,remark]
                        else:
                            raise ValueError("failed to recognize input!")
                except ValueError as v:
                    print(v)
                except Exception as e:
                    print(e)

        for i in range(self.taskCount):
            inpList = parsing()
            slno = inpList[0]
            if inpList =='q':
                break
            elif inpList[1].startswith('com') or inpList[1].startswith('succe') or inpList[1]=='done':
                status = "completed"
            elif inpList[1].startswith('inc') or inpList[1].startswith('fail'):
                status = "Failed"
            elif inpList[1].startswith('pending') or inpList[1].startswith('notc'):
                status = "Pending"
            if inpList[2] == ' ':
                self.overwrite_task(slno, status)
            remark = inpList[2]
            
            self.overwrite_task(slno, status,remark)

            


    def update_task(self): # governs the setup.
        print(">>> UPDATE TASKS <<<".center(60))
        self.data = self.data_handler.view_data(False)
        try:
            while True:
                self.updating_date = self.update_date()
                if self.updating_date == 'q':
                    break
                elif datetime.strptime(self.updating_date, "%Y-%m-%d"):
                    if self.view_tasks_to_update(data=self.data,update_date=self.updating_date):
                        self.parameter_of_task()
                        break
                    else:
                        print("Did you want to choose another date to update?")
                else:
                    print("there is some internal error....")
                    break

        except Exception as e:
            print(f"Error occured .. {e}\nat {__class__.__name__}/{self.update_task.__name__}")
                    


#update each user interactive loop's exception, in case if the user enters without typing any value.
# update the string sparcing in the parameter to update funcion so that the user shouldn't have to alway type / . make it more simple to use.
