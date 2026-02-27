class TaskViewer:
    def __init__(self,DataHandler):
        self.DataHandler = DataHandler

    def view_tasks(self):
        self.data = self.DataHandler.view_data(False)
        if self.DataHandler.display_data(self.data):
            print("Enter the Tasks first")
        else:
            pass


        
