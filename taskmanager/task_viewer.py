class TaskViewer:
    def __init__(self,DataHandler):
        self.DataHandler = DataHandler

    def view_tasks(self):
        data = self.DataHandler.view_data(False)
        self.DataHandler.display_data(data)
        
