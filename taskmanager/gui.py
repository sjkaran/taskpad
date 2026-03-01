import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk

class TaskPadGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("TaskPad")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Set appearance mode and theme for attractiveness
        ctk.set_appearance_mode("System")  # Light/Dark based on system
        ctk.set_default_color_theme("blue")  # Clean, modern blue theme
        
        # Main frame for padding and organization
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title label - simple and centered
        self.title_label = ctk.CTkLabel(self.main_frame, text="TaskPad", font=("Arial", 24))
        self.title_label.pack(pady=10)
        
        # Task display area - Treeview for minimalist table view
        self.task_tree = ttk.Treeview(self.main_frame, columns=("Date", "Task", "Status", "Remarks"), show="headings", height=10)
        self.task_tree.heading("Date", text="Date")
        self.task_tree.heading("Task", text="Task")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Remarks", text="Remarks")
        self.task_tree.column("Date", width=100)
        self.task_tree.column("Task", width=200)
        self.task_tree.column("Status", width=100)
        self.task_tree.column("Remarks", width=150)
        self.task_tree.pack(pady=10, fill="both", expand=True)
        
        # Buttons frame - horizontal layout for actions
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        self.view_btn = ctk.CTkButton(self.button_frame, text="View Tasks", command=self.view_tasks)
        self.view_btn.grid(row=0, column=0, padx=5)
        
        self.assign_btn = ctk.CTkButton(self.button_frame, text="Assign Task", command=self.assign_task)
        self.assign_btn.grid(row=0, column=1, padx=5)
        
        self.update_btn = ctk.CTkButton(self.button_frame, text="Update Task", command=self.update_task)
        self.update_btn.grid(row=0, column=2, padx=5)
        
        self.clear_btn = ctk.CTkButton(self.button_frame, text="Clear Task", command=self.clear_task)
        self.clear_btn.grid(row=0, column=3, padx=5)
        
        self.exit_btn = ctk.CTkButton(self.button_frame, text="Exit", command=self.root.quit)
        self.exit_btn.grid(row=0, column=4, padx=5)
        
        # Initial view load
        self.view_tasks()
        
        self.root.mainloop()
    
    def view_tasks(self):
        # Placeholder: Clear and load tasks
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Example data - INTEGRATE: Replace with data_handler.load_tasks() or similar
        # Assume tasks is a list of dicts: [{'id': 1, 'date': '2026-02-28', 'task': 'Sample', 'status': 'Pending', 'remarks': ''}]
        tasks = [
            (1, "2026-02-28", "Sample Task 1", "Pending", "No remarks"),
            (2, "2026-03-01", "Sample Task 2", "Completed", "Done on time")
        ]
        
        for task_id, date, task_desc, status, remarks in tasks:
            self.task_tree.insert("", "end", iid=task_id, values=(date, task_desc, status, remarks))
        
        # If no tasks, show message (optional)
        if not tasks:
            messagebox.showinfo("View Tasks", "No tasks available.")
    
    def assign_task(self):
        # Popup dialog for assigning task
        assign_window = ctk.CTkToplevel(self.root)
        assign_window.title("Assign Task")
        assign_window.geometry("300x200")
        assign_window.resizable(False, False)
        
        ctk.CTkLabel(assign_window, text="Task Description:").pack(pady=5)
        task_entry = ctk.CTkEntry(assign_window, width=250)
        task_entry.pack(pady=5)
        
        ctk.CTkLabel(assign_window, text="Assign for:").pack(pady=5)
        date_var = ctk.StringVar(value="Today")
        today_radio = ctk.CTkRadioButton(assign_window, text="Today", variable=date_var, value="Today")
        today_radio.pack()
        tomorrow_radio = ctk.CTkRadioButton(assign_window, text="Tomorrow", variable=date_var, value="Tomorrow")
        tomorrow_radio.pack()
        
        def submit_assign():
            task_desc = task_entry.get().strip()
            if not task_desc:
                messagebox.showwarning("Assign Task", "Task description cannot be empty.")
                return
            date = date_var.get()
            # INTEGRATE: Call task_assigner.assign_task(task_desc, date)
            # Placeholder success
            messagebox.showinfo("Assign Task", f"Task '{task_desc}' assigned for {date}.")
            assign_window.destroy()
            self.view_tasks()  # Refresh task list
        
        submit_btn = ctk.CTkButton(assign_window, text="Assign", command=submit_assign)
        submit_btn.pack(pady=10)
    
    def update_task(self):
        # Get selected task
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Update Task", "Please select a task to update.")
            return
        
        # Popup dialog for updating
        update_window = ctk.CTkToplevel(self.root)
        update_window.title("Update Task")
        update_window.geometry("300x200")
        update_window.resizable(False, False)
        
        ctk.CTkLabel(update_window, text="New Status:").pack(pady=5)
        status_var = ctk.StringVar(value="Pending")
        pending_radio = ctk.CTkRadioButton(update_window, text="Pending", variable=status_var, value="Pending")
        pending_radio.pack()
        completed_radio = ctk.CTkRadioButton(update_window, text="Completed", variable=status_var, value="Completed")
        completed_radio.pack()
        
        ctk.CTkLabel(update_window, text="Remarks:").pack(pady=5)
        remarks_entry = ctk.CTkEntry(update_window, width=250)
        remarks_entry.pack(pady=5)
        
        def submit_update():
            status = status_var.get()
            remarks = remarks_entry.get().strip()
            # INTEGRATE: Call task_updater.update_task(int(selected), status, remarks)
            # Placeholder success
            messagebox.showinfo("Update Task", f"Task updated to {status} with remarks '{remarks}'.")
            update_window.destroy()
            self.view_tasks()  # Refresh task list
        
        submit_btn = ctk.CTkButton(update_window, text="Update", command=submit_update)
        submit_btn.pack(pady=10)
    
    def clear_task(self):
        # Get selected task
        selected = self.task_tree.focus()
        if not selected:
            messagebox.showwarning("Clear Task", "Please select a task to clear.")
            return
        
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear this task?"):
            # INTEGRATE: Call task_clearer.clear_task(int(selected))
            # Placeholder success
            messagebox.showinfo("Clear Task", "Task cleared successfully.")
            self.view_tasks()  # Refresh task list

if __name__ == "__main__":
    TaskPadGUI()