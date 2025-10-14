from datetime import datetime, timedelta
class TaskAssigner:
    def __init__(self,data_handler):
        self.data_handler = data_handler
    
        
    def assign_task(self):
        # assing new tasks with proper data key initialization.

        data = self.data_handler.view_data(False)
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        def assigning(data,date_str,n):
                """Inner fuction to handle task assignment"""
                try:
                    current_tasks = data["tasks"].get(date_str,{})
                    data["tasks"][date_str] = current_tasks
                    next_num = len(current_tasks) + 1 if current_tasks else 1

                    print(f"\nAssigning {n} tasks for {date_str}:")
                    for i in range(n):
                        tasks_input = input(f"Enter task - {i+1}:  ").strip()
                        if not tasks_input:
                            return False
                        else:
                            data["tasks"][date_str][str(next_num + i)]={
                                'task':tasks_input,
                                'result':'PENDING',
                                'remark':''
                            }
                    return True
                except Exception as e:
                    print(f"Error occured during assignment: {e}")
                    return False
        try:
            while True:
                try:
                    numOfTasks = int(input("Enter the number of tasks you want to assign: "))
                    if numOfTasks==0: break
                    elif numOfTasks <= 0 or numOfTasks >=10:
                        print("Please enter a number between 1 and 9.")
                        continue

                    userDate = input("Do you want to assign your tasks for today?   ").strip()

                    if userDate.lower().startswith('y'):
                        if assigning(data, today, numOfTasks):
                            if self.data_handler.upload_data(data):
                                print(f"✅ {numOfTasks} tasks assigned for today ({today})")
                            else:
                                print("Error saving tasks.")
                            break
                    elif userDate.lower().startswith('n'):
                        if assigning(data, tomorrow, numOfTasks):
                            if self.data_handler.upload_data(data):
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
