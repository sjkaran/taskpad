from taskmanager1 import taskmanager1

if __name__=="__main__":
    try:
        taskmanager1 = taskmanager1()
        taskmanager1.control_unit()

    except Exception as e:
        print(f"Error starting application: {e}")