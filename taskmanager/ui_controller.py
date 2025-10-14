
class UIController:
    def __init__(self, data_handler, task_assigner, task_updater, task_clearer ):
        self.data_handler = data_handler
        self.task_assigner = task_assigner
        self.task_updater = task_updater
        self.task_clearer = task_clearer

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
                    inp= input("Enter your choice : ").strip().lower()
                    match inp:
                        case str() if inp =='1' or inp.startswith('v'):
                            print("\n📃 CURRENT TASKS: ")
                            print("-"*40)
                            self.data_handler.view_data(True)

                        case str() if inp == '2' or inp.startswith('as'):
                            print("\n➕ ASSIGNING NEW TASKS:")
                            print("-"*40)
                            self.task_assigner.assign_task()

                        case str() if inp =='3' or inp.startswith('up'):
                            print("\n◴ UPDATE TASKS:")
                            print("-"*40)
                            self.task_updater.update_task()

                        case str() if inp=='4' or inp.startswith('cl'):
                            print("\n🧹 CLEAR TASKS:")
                            print("-"*40)
                            self.task_clearer.clean_ui_controler()
                        
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
            print(e)


'''
* include custom settings to design the task manager accordingly.
    > tasks will get time of two days or more if they weren't completed in time.
    > tasks will automatically resulted as failded if couldn't completed in time and saved into another file.
    > keep a track of the task completion rate and faluer rate.
'''