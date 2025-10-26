class TaskClearer:
    def __init__(self,data_handler):
        self.data_handler = data_handler


    def date_wize_cleaner(self):
        data=self.data_handler.view_data(False)
        try:
            inpdate=input("enter the date of which you want to clear all tasks:  ")
            if len(inpdate)<10:
                print("enter the date in dd-mm-yyyy format.")
                return False
            elif inpdate not in data["tasks"]:
                print(f"there is no tasks assigned to {inpdate}")
                return False
            elif len(data["tasks"][inpdate])>0:
                del data["tasks"][inpdate]
                self.data_handler.upload_data(data)
                print(f"tasks of {inpdate} are successfully cleared...")
                return True
            else:
                print(f"there is no tasks to clean in {inpdate}")
                return False
        except Exception as e:
            print(f"error occured in {__class__.__name__}/{self.date_wize_cleaner.__name__}")
            return False
        
    def result_wize_cleaner(self):
        def clear_task(data,remark):
            dellist=[]
            for d in data["tasks"]:
                for t in data["tasks"][d]:
                    if data["tasks"][d][t]["result"]==remark:
                        dellist.append((d,t))

            if len(dellist)==0:
                print(f"No task is found to be {remark}")
            else:
                for i in dellist:
                    del data["tasks"][i[0]][i[1]]
                    if len(data["tasks"][i[0]])==0:
                        del data["tasks"][i[0]]
                    print("cleaning completed")
                    print(f"total {len(dellist)} tasks cleaned.")
                    dellist=[]
                    self.data_handler.upload_data(data)


        data=self.data_handler.view_data(False)
        remarks=["COMPLETED","PENDING"]
        try:
            inp=input(f"Clear tasks which are {remarks[0]} or {remarks[1]}    ")
            if inp.startswith('c'):
                clear_task(data,remarks[0])
            elif inp.startswith('p'):
                clear_task(data,remark=remarks[1])
            else:
                return
        except KeyboardInterrupt as k:
            print(f"{k} in loc: {__class__.__name__}/{self.result_wize_cleaner.__name__}")
        except Exception as e:
            print(f"{e} in loc: {__class__.__name__}/{self.result_wize_cleaner.__name__}")


    def manual_cleaner(self):
       #mannually clears tasks by showing them and asking the task number.
       pass


    def clean_ui_controler(self):
        def options():
            print("\nHow you wanna remove the tasks: ")
            print("1. remove out dated tasks.")
            print("2. remove completed tasks.")
            print("3. remove tasks manually.")
            print("4. go back to menu.\n")
            try:
                inp = input("")
                return inp
            except Exception as e:
                print(f"{e}\nloc: {__class__.__name__}/{options.__name__}")

        def final_clean_ui():            
            while True:
                try:
                    ipt = options()
                    match ipt:
                        case m if m in ('1','rm out','remove out dated','out'):
                            print("activate date wize cleaner.")
                            date_wise=self.date_wize_cleaner()
                            if date_wise:
                                break
                            else:
                                print("try again...")

                        case m if m in ('2','rm comp','completed','complete'):
                            print("activate date wize cleaner.")
                            self.result_wize_cleaner()

                        case m if m in ('3','remove manualy','manualy','rm man'):
                            print("activate the manual cleaner:")
                            self.manual_cleaner()
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
        
        data = self.data_handler.view_data(False)
        if self.data_handler.check_data():
            self.data_handler.display_data(self.data_handler.view_data(False))
            final_clean_ui()
        else:
            print("- "*10,end="-")
            print("Assign the task first",end="-")
            print("- "*10,end="-")