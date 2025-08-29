import os
import json

class DataHandler:
    def __init__(self,filename="task_base.json"):
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
        
    def view_data(self, displays: bool):
        try:
            with open(self.filename, "r") as f:
                loaded_data = json.load(f)
            if displays:
                self.display_data(loaded_data)
            return loaded_data
        except FileNotFoundError:
            print(f"Error: file {self.filename} not found. loc: {self.view_data.__name__} / {self.__class__.__name__}")
            return {"tasks":{}}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.filename}. loc: {self.view_data.__name__} / {self.__class__.__name__}")
            return {"tasks":{}}
        
    def upload_data(self,newdata):
        try:
            with open(self.filename,"w")as file:
                json.dump(newdata, file, indent=4)
            return True
        except Exception as e:
            print(f"Error in saving data: loc : {self.upload_data.__name__} / {self.__class__.__name__}")

    def display_data(self, data):
        if len(data["tasks"])>0:
            for dates in data["tasks"]:
                print(f"\nDate: {dates}")
                for n in data["tasks"][dates]:
                    num = data["tasks"][dates][n]
                    print(f"{n}. {num['task']}\t{num['result']}\n{num['remark']}")
        else:
            print("\nNo task found. start by assigning some tasks!")
