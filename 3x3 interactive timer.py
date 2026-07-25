import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import json
import os
from datetime import datetime

class SpeedCubeTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("3x3 Speed Cube Timer")
        self.root.geometry("600x500")
        self.root.configure(bg="#1a1a1a")
        
        # Timer variables
        self.running = False
        self.elapsed_time = 0
        self.start_time = None
        self.times_list = []
        self.times_file = "3x3_times.json"
        
        # Inspection/Looking time variables
        self.phase = "idle"  # idle, inspection, grace, ready, solving
        self.inspection_start = None
        self.inspection_time = 15000  # 15 seconds in milliseconds
        self.grace_time = 3000  # 3 seconds in milliseconds
        
        # Load previous times
        self.load_times()
        
        # Main frame
        main_frame = tk.Frame(root, bg="#1a1a1a")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="3x3 Speed Cube Timer", 
                        font=("Arial", 24, "bold"), bg="#1a1a1a", fg="#00ff00")
        title.pack(pady=10)
        
        # Timer display
        self.timer_label = tk.Label(main_frame, text="00:00.00", 
                                   font=("Arial", 100, "bold"), 
                                   bg="#1a1a1a", fg="#00ff00")
        self.timer_label.pack(pady=20)
        
        # Status display
        self.status_label = tk.Label(main_frame, text="Press any key to START looking time", 
                                    font=("Arial", 16), bg="#1a1a1a", fg="#ffff00")
        self.status_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg="#1a1a1a")
        button_frame.pack(pady=20)
        
        # View times button
        view_btn = tk.Button(button_frame, text="View Times", command=self.view_times,
                            font=("Arial", 12), bg="#0066ff", fg="white", 
                            padx=10, pady=10, cursor="hand2")
        view_btn.grid(row=0, column=0, padx=10)
        
        # Clear times button
        clear_btn = tk.Button(button_frame, text="Clear Times", command=self.clear_times,
                             font=("Arial", 12), bg="#ff0000", fg="white",
                             padx=10, pady=10, cursor="hand2")
        clear_btn.grid(row=0, column=1, padx=10)
        
        # Info
        info = tk.Label(main_frame, 
                       text="Press ANY KEY to Start\nPress ANY KEY to Stop\nPress ESC to Exit",
                       font=("Arial", 12), bg="#1a1a1a", fg="#cccccc",
                       justify=tk.CENTER)
        info.pack(pady=20)
        
        # Bind keys
        self.root.bind('<Key>', self.key_press)
        self.root.bind('<Escape>', self.exit_app)
        
        # Update timer
        self.update_timer()
    
    def format_time(self, milliseconds):
        """Convert milliseconds to MM:SS.MS format"""
        milliseconds = int(milliseconds)
        seconds = milliseconds // 1000
        ms = (milliseconds % 1000) // 10
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}.{ms:02d}"
    
    def key_press(self, event):
        """Handle any key press to start/stop timer"""
        if event.keysym == "Escape":
            return
        
        if self.phase == "idle":
            # Start inspection phase
            self.phase = "inspection"
            self.inspection_start = time.time()
            self.status_label.config(text="LOOKING TIME: 12 seconds", fg="#00ff00")
        
        elif self.phase == "inspection":
            # User pressed key during inspection, cancel it
            self.phase = "idle"
            self.inspection_start = None
            self.status_label.config(text="Cancelled. Press any key to START looking time", fg="#ffff00")
        
        elif self.phase == "grace":
            # User pressed key during grace period, cancel it
            self.phase = "idle"
            self.inspection_start = None
            self.status_label.config(text="Cancelled. Press any key to START looking time", fg="#ffff00")
        
        elif self.phase == "ready":
            # Start solving
            self.phase = "solving"
            self.running = True
            self.start_time = time.time()
            self.elapsed_time = 0
            self.status_label.config(text="SOLVING... Press any key to STOP", fg="#00ff00")
        
        elif self.phase == "solving":
            # Stop solving
            self.running = False
            self.phase = "idle"
            solve_time = self.elapsed_time
            self.times_list.append({
                'time': solve_time,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.save_times()
            self.status_label.config(text="Solve Stopped! Press any key to START looking time", fg="#ffff00")
            
            # Ask if user wants to see times
            self.ask_show_times(solve_time)
    
    def ask_show_times(self, solve_time):
        """Ask user if they want to see the times list"""
        response = messagebox.askyesno("Solve Complete!", 
                                       f"Solve Time: {self.format_time(solve_time)}\n\nView your times?")
        if response:
            self.view_times()
    
    def update_timer(self):
        """Update the timer display"""
        if self.running:
            self.elapsed_time = int((time.time() - self.start_time) * 1000)
            self.timer_label.config(text=self.format_time(self.elapsed_time))
        
        # Handle inspection phase
        if self.phase == "inspection":
            elapsed = int((time.time() - self.inspection_start) * 1000)
            remaining = self.inspection_time - elapsed
            
            if remaining > 0:
                self.timer_label.config(text=self.format_time(remaining), fg="#ffaa00")
            else:
                # Move to grace period
                self.phase = "grace"
                self.inspection_start = time.time()
                self.status_label.config(text="READY TO SOLVE: 3 seconds", fg="#0099ff")
        
        elif self.phase == "grace":
            elapsed = int((time.time() - self.inspection_start) * 1000)
            remaining = self.grace_time - elapsed
            
            if remaining > 0:
                self.timer_label.config(text=self.format_time(remaining), fg="#0099ff")
            else:
                # Move to ready phase
                self.phase = "ready"
                self.timer_label.config(text="00:00.00", fg="#00ff00")
                self.status_label.config(text="PRESS ANY KEY TO START SOLVING", fg="#ff0000")
        
        elif self.phase == "ready":
            self.timer_label.config(text="00:00.00", fg="#00ff00")
        
        elif self.phase == "idle" and not self.running:
            self.timer_label.config(text="00:00.00", fg="#00ff00")
        
        self.root.after(10, self.update_timer)
    
    def view_times(self):
        """Display all recorded times with color coding"""
        if not self.times_list:
            messagebox.showinfo("Times", "No times recorded yet!")
            return
        
        # Create new window
        times_window = tk.Toplevel(self.root)
        times_window.title("3x3 Solve Times")
        times_window.geometry("700x600")
        times_window.configure(bg="#1a1a1a")
        
        # Title
        title = tk.Label(times_window, text="Your Solve Times", 
                        font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#00ff00")
        title.pack(pady=10)
        
        # Calculate statistics
        times_in_ms = [entry['time'] for entry in self.times_list]
        avg_time = sum(times_in_ms) / len(times_in_ms)
        best_time = min(times_in_ms)
        worst_time = max(times_in_ms)
        
        # Main frame with scrollbar
        main_frame = tk.Frame(times_window, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(main_frame, bg="#0a0a0a", highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0a0a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Statistics section
        stats_frame = tk.Frame(scrollable_frame, bg="#0a0a0a")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(stats_frame, text="═"*50, font=("Arial", 10), bg="#0a0a0a", fg="#666666").pack()
        tk.Label(stats_frame, text=f"Total Solves: {len(self.times_list)}", 
                font=("Arial", 12, "bold"), bg="#0a0a0a", fg="#ffffff").pack(anchor="w")
        tk.Label(stats_frame, text=f"Best: {self.format_time(best_time)}", 
                font=("Arial", 12, "bold"), bg="#0a0a0a", fg="#00ff00").pack(anchor="w")
        tk.Label(stats_frame, text=f"Worst: {self.format_time(worst_time)}", 
                font=("Arial", 12, "bold"), bg="#0a0a0a", fg="#ff0000").pack(anchor="w")
        tk.Label(stats_frame, text=f"Average: {self.format_time(avg_time)}", 
                font=("Arial", 12, "bold"), bg="#0a0a0a", fg="#ffff00").pack(anchor="w")
        tk.Label(stats_frame, text="═"*50, font=("Arial", 10), bg="#0a0a0a", fg="#666666").pack()
        
        # Solves list
        tk.Label(scrollable_frame, text="All Solves:", font=("Arial", 12, "bold"), 
                bg="#0a0a0a", fg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
        
        for i, entry in enumerate(self.times_list):
            solve_time = entry['time']
            time_str = self.format_time(solve_time)
            date_str = entry['date']
            
            # Determine color based on solve time
            if solve_time == best_time:
                color = "#00ff00"  # Green for best
            elif solve_time == worst_time:
                color = "#ff0000"  # Red for worst
            elif solve_time >= 40000:  # 40 seconds or more
                color = "#8B4513"  # Brown
            else:  # Under 40 seconds
                color = "#ffff00"  # Light yellow (RGB 255:255:124)
            
            # Create frame for each solve with delete button
            solve_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
            solve_frame.pack(fill=tk.X, padx=10, pady=3)
            
            # Solve info label
            solve_label = tk.Label(solve_frame, 
                                  text=f"{i+1}. {time_str} - {date_str}",
                                  font=("Arial", 11), bg="#1a1a1a", fg=color, anchor="w")
            solve_label.pack(side="left", fill=tk.X, expand=True)
            
            # Delete button
            delete_btn = tk.Button(solve_frame, text="✕", 
                                  command=lambda idx=i: self.delete_solve(idx, times_window),
                                  font=("Arial", 10), bg="#ff4444", fg="white",
                                  padx=5, pady=0, cursor="hand2", bd=0)
            delete_btn.pack(side="right", padx=5)
    
    def delete_solve(self, index, times_window):
        """Delete a specific solve and refresh the view"""
        response = messagebox.askyesno("Delete Solve", 
                                       f"Delete solve: {self.format_time(self.times_list[index]['time'])}?")
        if response:
            del self.times_list[index]
            self.save_times()
            times_window.destroy()
            self.view_times()
    
    def clear_times(self):
        """Clear all recorded times"""
        response = messagebox.askyesno("Clear Times", 
                                       "Are you sure you want to clear all times?")
        if response:
            self.times_list = []
            self.save_times()
            messagebox.showinfo("Success", "All times cleared!")
            self.elapsed_time = 0
            self.running = False
            self.phase = "idle"
            self.status_label.config(text="Press any key to START looking time", fg="#ffff00")
    
    def save_times(self):
        """Save times to JSON file"""
        with open(self.times_file, 'w') as f:
            json.dump(self.times_list, f, indent=2)
    
    def load_times(self):
        """Load times from JSON file"""
        if os.path.exists(self.times_file):
            try:
                with open(self.times_file, 'r') as f:
                    self.times_list = json.load(f)
            except:
                self.times_list = []
        else:
            self.times_list = []
    
    def exit_app(self, event):
        """Exit the application"""
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedCubeTimer(root)
    root.mainloop()
