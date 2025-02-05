# File: demo_panda3d

import tkinter as tk  # (built-in; comes with Python)
from tkinter import messagebox  # (built-in)
import os  # (built-in)
import glob  # (built-in)
import subprocess  # (built-in)
import threading  # (built-in)
import time  # (built-in)
import sys  # (built-in)

def find_py_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.abspath(os.path.join(root, file))
                py_files.append(full_path)
    return py_files

class DemoRunnerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Panda3D Demo Launcher")
        
        # List of absolute paths of demo programs
        self.programs = []
        # Index pointer for running all demos
        self.current_index = 0
        # Flag indicating whether we're in "Run All" mode
        self.running_all = False
        # Flag to stop the sequence after current demo exits
        self.stop_flag = False
        # Holds the currently running process (if any)
        self.current_process = None
        # Log file handle (will be recreated at each run sequence)
        self.log_file = None

        # Create a Listbox to show the demo files
        self.listbox = tk.Listbox(root, width=100)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Frame to hold the control buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        # "Run" button to run a single selected demo
        self.run_button = tk.Button(btn_frame, text="Run", command=self.run_selected)
        self.run_button.pack(side=tk.LEFT, padx=5, pady=5)
        # "Run All" button to automatically run all demos sequentially
        self.run_all_button = tk.Button(btn_frame, text="Run All", command=self.run_all)
        self.run_all_button.pack(side=tk.LEFT, padx=5, pady=5)
        # "Stop" button to cancel further auto-running (does not kill the current process)
        self.stop_button = tk.Button(btn_frame, text="Stop", command=self.stop_running, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Load the demo programs from the Demo folder
        self.load_programs()

    def load_programs(self):
        """Scan the 'Demo' folder for Python files (excluding demo.py) and populate the listbox."""
        demo_folder = os.path.abspath(os.path.dirname(__file__) + "\\..")
        if not os.path.exists(demo_folder):
            messagebox.showerror("Error", f"Demo folder not found: {demo_folder}")
            return
        # Find all .py files in the folder
        files = find_py_files(demo_folder)
        # Exclude any file named 'demo.py' (case-insensitive)
        self.programs = [os.path.abspath(f) for f in files if os.path.basename(f).lower() != "demo.py" and os.path.basename(f).lower() != "setup.py"]
        self.programs.sort()
        self.listbox.delete(0, tk.END)
        for p in self.programs:
            self.listbox.insert(tk.END, p)

    def run_selected(self):
        """Run a single demo selected in the listbox."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a program to run.")
            return
        index = selection[0]
        self.current_index = index
        self.running_all = False  # Single run mode
        self.prepare_run()  # Disable controls and create a fresh log file
        self.run_program(self.programs[index], index, self.on_run_complete)

    def run_all(self):
        """Run all demos sequentially."""
        if not self.programs:
            messagebox.showwarning("No Programs", "No demo programs found.")
            return
        self.current_index = 0
        self.running_all = True  # Run All mode
        self.stop_flag = False
        self.prepare_run()
        self.stop_button.config(state=tk.NORMAL)  # Allow user to stop after current demo
        self.run_next()

    def stop_running(self):
        """Set a flag to stop running further demos after the current one closes."""
        self.stop_flag = True
        self.stop_button.config(state=tk.DISABLED)
        # Note: The current demo is not terminated; user must close it manually.

    def prepare_run(self):
        """Disable run controls and create a new demo.log file for this run sequence."""
        self.run_button.config(state=tk.DISABLED)
        self.run_all_button.config(state=tk.DISABLED)
        # Create (or overwrite) demo.log in the current directory
        self.log_file = open("demo.log", "w")

    def finish_run(self):
        """Re-enable controls and close the log file."""
        self.run_button.config(state=tk.NORMAL)
        self.run_all_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    def run_next(self):
        """Run the next demo in the list if available and if not stopped."""
        if self.current_index >= len(self.programs) or self.stop_flag:
            self.finish_run()
            return
        # Highlight the current demo in the listbox
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.current_index)
        self.listbox.activate(self.current_index)
        program_path = self.programs[self.current_index]
        self.run_program(program_path, self.current_index, self.on_run_complete)

    def run_program(self, program_path, index, callback):
        """
        Launch the specified demo program in a separate thread,
        log its execution, and invoke callback when done.
        """
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.write_log(f"=== Starting program: {program_path} at {start_time} ===\n")

        def target():
            try:
                # Launch the demo program using the same Python interpreter.
                proc = subprocess.Popen(
                    [sys.executable, program_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.current_process = proc
                # Wait for the process to finish and capture output.
                stdout, stderr = proc.communicate()
                self.current_process = None
                self.write_log(f"--- Output for program: {program_path} ---\n")
                if stdout:
                    self.write_log("STDOUT:\n" + stdout + "\n")
                if stderr:
                    self.write_log("STDERR:\n" + stderr + "\n")
            except Exception as e:
                self.write_log(f"Exception occurred: {str(e)}\n")
            # Schedule the callback to run on the main thread.
            self.root.after(0, callback)

        # Run the blocking process call in a separate thread.
        thread = threading.Thread(target=target)
        thread.start()

    def on_run_complete(self):
        """Callback when a demo program finishes execution."""
        if self.running_all:
            self.current_index += 1
            # Short delay before launching the next demo.
            self.root.after(500, self.run_next)
        else:
            # In single run mode, re-enable controls when done.
            self.finish_run()

    def write_log(self, message):
        """Write a message to demo.log and flush immediately."""
        if self.log_file:
            self.log_file.write(message)
            self.log_file.flush()

if __name__ == "__main__":
    root = tk.Tk()
    app = DemoRunnerGUI(root)
    root.mainloop()
