# This is an all-in-one copy-pastable code file for quickly copying the whole codebase as one .py file
# Copy all the contents from this file and run the code; all libraries are built in with Python
# make sure you have Python 3.10+

import copy
import tkinter as tk
from tkinter import messagebox
import time
import json
import os
import sys
import random
from datetime import datetime
import tempfile
import shutil

MOVES = ["U", "D", "L", "R", "F", "B"]
MODIFIERS = ["", "'", "2"]

# Face indices: U=0, D=1, F=2, B=3, L=4, R=5
# Each face: 9 stickers [0..8] in reading order (top-left to bottom-right)
# Standard Western Color Scheme
FACE_COLORS = {
    "U": "#ffffff",  # white
    "D": "#ffff00",  # yellow
    "F": "#00aa00",  # green
    "B": "#0055ff",  # blue
    "L": "#ff8800",  # orange
    "R": "#ff0000",  # red
}

def make_solved_cube():
    return {f: [f]*9 for f in "UDFBLR"}

def rotate_face_cw(cube, f):
    s = cube[f]
    cube[f] = [s[6],s[3],s[0], s[7],s[4],s[1], s[8],s[5],s[2]]

def rotate_face_ccw(cube, f):
    rotate_face_cw(cube, f)
    rotate_face_cw(cube, f)
    rotate_face_cw(cube, f)

def apply_move(cube, move):
    face = move[0]
    mod  = move[1:]
    times = 3 if mod == "'" else (2 if mod == "2" else 1)
    for _ in range(times):
        _do_move(cube, face)

def _do_move(cube, face):
    rotate_face_cw(cube, face)
    U,D,F,B,L,R = (cube[x] for x in "UDFBLR")
    
    if face == "U":
        # CW from above: L-top -> B-top -> R-top -> F-top -> L-top
        tmp = [F[0],F[1],F[2]]
        F[0],F[1],F[2] = R[0],R[1],R[2]
        R[0],R[1],R[2] = B[0],B[1],B[2]
        B[0],B[1],B[2] = L[0],L[1],L[2]
        L[0],L[1],L[2] = tmp
    elif face == "D":
        # CW from below: L-bot -> F-bot -> R-bot -> B-bot -> L-bot
        tmp = [F[6],F[7],F[8]]
        F[6],F[7],F[8] = L[6],L[7],L[8]
        L[6],L[7],L[8] = B[6],B[7],B[8]
        B[6],B[7],B[8] = R[6],R[7],R[8]
        R[6],R[7],R[8] = tmp
    elif face == "F":
        # CW from front: U-bot -> R-left -> D-top -> L-right -> U-bot
        tmp = [U[6],U[7],U[8]]
        U[6],U[7],U[8] = L[8],L[5],L[2]
        L[2],L[5],L[8] = D[0],D[1],D[2]
        D[0],D[1],D[2] = R[6],R[3],R[0]
        R[0],R[3],R[6] = tmp
    elif face == "B":
        # CW from back: U-top -> L-left -> D-bot -> R-right -> U-top
        tmp = [U[0],U[1],U[2]]
        U[0],U[1],U[2] = R[2],R[5],R[8]
        R[2],R[5],R[8] = D[8],D[7],D[6]
        D[6],D[7],D[8] = L[0],L[3],L[6]
        L[0],L[3],L[6] = tmp[::-1]
    elif face == "L":
        # CW from left: U-left -> F-left -> D-left -> B-right -> U-left
        tmp = [U[0],U[3],U[6]]
        U[0],U[3],U[6] = B[8],B[5],B[2]
        B[2],B[5],B[8] = D[6],D[3],D[0]
        D[0],D[3],D[6] = F[0],F[3],F[6]
        F[0],F[3],F[6] = tmp
    elif face == "R":
        # CW from right: U-right -> B-left -> D-right -> F-right -> U-right
        tmp = [U[2],U[5],U[8]]
        U[2],U[5],U[8] = F[2],F[5],F[8]
        F[2],F[5],F[8] = D[2],D[5],D[8]
        D[2],D[5],D[8] = B[6],B[3],B[0]
        B[0],B[3],B[6] = tmp[::-1]

def open_visualizer(parent, scramble_str):
    moves = scramble_str.split()
    win = tk.Toplevel(parent)
    win.title("Scramble Visualizer")
    win.configure(bg="#1a1a1a")
    win.geometry("600x540")

    move_label = tk.Label(win, text="", font=("Arial", 16, "bold"),
                          bg="#1a1a1a", fg="#ff9900")
    move_label.pack(pady=(12, 2))

    seq_label = tk.Label(win, text="", font=("Courier", 11),
                         bg="#1a1a1a", fg="#555555", wraplength=560, justify="center")
    seq_label.pack(pady=(0, 4))

    nav_label = tk.Label(win, text="\u2190 \u2192  arrow keys to step through moves",
                         font=("Arial", 10), bg="#1a1a1a", fg="#666666")
    nav_label.pack(pady=(0, 6))

    canvas = tk.Canvas(win, bg="#1a1a1a", highlightthickness=0, width=600, height=340)
    canvas.pack()

    def shade(color, factor):
        r = int(int(color[1:3], 16) * factor)
        g = int(int(color[3:5], 16) * factor)
        b = int(int(color[5:7], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_cube(cube):
        canvas.delete("all")
        
        # Sizing and center point where U, F, and R faces meet
        S = 36
        S2 = 18
        CX, CY = 300, 220

        def add(p1, p2): return (p1[0] + p2[0], p1[1] + p2[1])
        def scale(v, f): return (v[0] * f, v[1] * f)

        # Isometric basis vectors
        vec_DL = (-S, S2)    # Down-Left
        vec_UR = (S, -S2)    # Up-Right
        vec_UL = (-S, -S2)   # Up-Left
        vec_DR = (S, S2)     # Down-Right
        vec_D  = (0, S)      # Down

        def draw_face(face_name, orig, vec_c, vec_r, color_darken):
            for row in range(3):
                for col in range(3):
                    idx = row * 3 + col
                    # Calculate 4 corners of the polygon sticker
                    p0 = add(orig, add(scale(vec_c, col), scale(vec_r, row)))
                    p1 = add(p0, vec_c)
                    p2 = add(p1, vec_r)
                    p3 = add(p0, vec_r)

                    color = FACE_COLORS[cube[face_name][idx]]
                    if color_darken != 1.0:
                        color = shade(color, color_darken)

                    canvas.create_polygon([p0, p1, p2, p3], fill=color, outline="#111", width=2)

        # R face (Right side, Red)
        R_orig = (CX, CY)
        draw_face("R", R_orig, vec_UR, vec_D, 0.75)

        # F face (Front side, drawn on Left, Green)
        F_orig = add((CX, CY), scale(vec_UL, 3))
        draw_face("F", F_orig, vec_DR, vec_D, 0.88)

        # U face (Top side, White)
        U_orig = (CX, CY - 3 * S)
        draw_face("U", U_orig, vec_DR, vec_DL, 1.0)

    # Pre-compute all states
    cube_states = [make_solved_cube()]
    for m in moves:
        nxt = copy.deepcopy(cube_states[-1])
        apply_move(nxt, m)
        cube_states.append(nxt)

    step_idx = [0]

    def refresh():
        idx = step_idx[0]
        draw_cube(cube_states[idx])
        if idx == 0:
            move_label.config(text="Solved state", fg="#aaaaaa")
            seq_label.config(text=" ".join(moves))
        elif idx == len(moves):
            move_label.config(text="Done!", fg="#00ff00")
            seq_label.config(text=" ".join(moves))
        else:
            move_label.config(text=f"Move {idx}/{len(moves)}: {moves[idx-1]}", fg="#ff9900")
            parts = [f"[{m}]" if i == idx-1 else m for i, m in enumerate(moves)]
            seq_label.config(text=" ".join(parts))

    def on_key(event):
        if event.keysym == "Right" and step_idx[0] < len(moves):
            step_idx[0] += 1
            refresh()
        elif event.keysym == "Left" and step_idx[0] > 0:
            step_idx[0] -= 1
            refresh()

    win.bind("<Key>", on_key)
    refresh()

def generate_scramble(length=20):
    scramble = []
    last = None
    for _ in range(length):
        available = [m for m in MOVES if m != last]
        move = random.choice(available)
        mod = random.choice(MODIFIERS)
        scramble.append(move + mod)
        last = move
    return " ".join(scramble)

def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

def data_path(relative_path):
    base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

class SpeedCubeTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("3x3 Speed Cube Timer")
        self.root.configure(bg="#1a1a1a")
        
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1024x768")
            
        self.running = False
        self.elapsed_time = 0
        self.start_time = None
        self.times_list = []
        self.times_file = data_path("3x3_times.json")
        
        self.phase = "idle"
        self.inspection_start = None
        self.inspection_time = 15000
        self.grace_time = 3000
        self.current_scramble = generate_scramble()
        
        self.times_window = None

        self.load_times()
        
        main_frame = tk.Frame(root, bg="#1a1a1a")
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        title = tk.Label(main_frame, text="3x3 Speed Cube Timer", 
                        font=("Arial", 24, "bold"), bg="#1a1a1a", fg="#00ff00")
        title.pack(pady=10)

        self.scramble_frame = tk.Frame(main_frame, bg="#1a1a1a")
        self.scramble_frame.pack(pady=(0, 5))

        self.new_scramble_btn = tk.Button(self.scramble_frame, text="New Scramble",
                                          command=self.new_scramble,
                                          font=("Arial", 10), bg="#333333", fg="#00cfff",
                                          padx=6, pady=3, cursor="hand2", relief="flat")
        self.visualize_btn = tk.Button(self.scramble_frame, text="Visualize Scramble",
                                       command=lambda: open_visualizer(self.root, self.current_scramble),
                                       font=("Arial", 10), bg="#333333", fg="#ff9900",
                                       padx=6, pady=3, cursor="hand2", relief="flat")
        
        self.scramble_label = tk.Label(self.scramble_frame, text="",
                                       font=("Courier", 13, "bold"), bg="#1a1a1a", fg="#00cfff",
                                       wraplength=1200, justify=tk.CENTER)

        self.timer_label = tk.Label(main_frame, text="00:00.00",
                                   font=("Arial", 100, "bold"),
                                   bg="#1a1a1a", fg="#00ff00")
        self.timer_label.pack(pady=20)

        self.status_label = tk.Label(main_frame, text="Press SPACE to see scramble",
                                    font=("Arial", 16), bg="#1a1a1a", fg="#ffff00")
        self.status_label.pack(pady=10)
        
        button_frame = tk.Frame(main_frame, bg="#1a1a1a")
        button_frame.pack(pady=20)
        
        view_btn = tk.Button(button_frame, text="View Times", command=self.view_times,
                            font=("Arial", 12), bg="#0066ff", fg="white", 
                            padx=10, pady=10, cursor="hand2")
        view_btn.grid(row=0, column=0, padx=10)
        
        clear_btn = tk.Button(button_frame, text="Clear Times", command=self.clear_times,
                             font=("Arial", 12), bg="#ff0000", fg="white",
                             padx=10, pady=10, cursor="hand2")
        clear_btn.grid(row=0, column=1, padx=10)
        
        info = tk.Label(main_frame, 
                       text="Press SPACE to Start\nPress SPACE to Stop\nPress ESC to Cancel\nPress ESC to Exit",
                       font=("Arial", 12), bg="#1a1a1a", fg="#cccccc",
                       justify=tk.CENTER)
        info.pack(pady=20)
        
        self.root.bind('<space>', self.key_press)
        self.root.bind('<Escape>', self.exit_or_cancel)
        
        self.update_timer()
    
    def format_time(self, milliseconds):
        milliseconds = int(milliseconds)
        seconds = milliseconds // 1000
        ms = (milliseconds % 1000) // 10
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}.{ms:02d}"
    
    def key_press(self, event):
        if self.phase == "idle":
            self.phase = "scramble_reveal"
            self.scramble_label.config(text=self.current_scramble)
            self.scramble_label.pack(pady=(4, 0))
            self.new_scramble_btn.pack(side="left", padx=6, pady=4)
            self.visualize_btn.pack(side="left", padx=6, pady=4)
            self.status_label.config(text="Press SPACE to START inspection time", fg="#ffff00")

        elif self.phase == "scramble_reveal":
            self.phase = "inspection"
            self.scramble_label.pack_forget()
            self.new_scramble_btn.pack_forget()
            self.visualize_btn.pack_forget()
            self.inspection_start = time.perf_counter()
            self.status_label.config(text="INSPECTION: 15 seconds", fg="#00ff00")
        
        elif self.phase == "inspection":
            pass

        elif self.phase == "grace":
            pass
        
        elif self.phase == "ready":
            self.phase = "solving"
            self.running = True
            self.start_time = time.perf_counter()
            self.elapsed_time = 0
            self.status_label.config(text="SOLVING... Press SPACE to STOP", fg="#00ff00")
        
        elif self.phase == "solving":
            self.running = False
            self.phase = "idle"
            solve_time = self.elapsed_time
            if solve_time > 0:
                self.times_list.append({
                    'time': solve_time,
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'scramble': self.current_scramble
                })
                self.save_times()
            self.current_scramble = generate_scramble()
            self.scramble_label.pack_forget()
            self.new_scramble_btn.pack_forget()
            self.visualize_btn.pack_forget()
            self.status_label.config(text="Solve Stopped! Press SPACE to see scramble", fg="#ffff00")
            if solve_time > 0:
                self.ask_show_times(solve_time)
    
    def exit_or_cancel(self, event):
        if self.phase == "inspection" or self.phase == "grace":
            self.phase = "idle"
            self.inspection_start = None
            self.scramble_label.pack_forget()
            self.new_scramble_btn.pack_forget()
            self.visualize_btn.pack_forget()
            self.status_label.config(text="Cancelled. Press SPACE to see scramble", fg="#ffff00")
        elif self.phase == "solving":
            self.running = False
            self.phase = "idle"
            self.scramble_label.pack_forget()
            self.new_scramble_btn.pack_forget()
            self.visualize_btn.pack_forget()
            self.status_label.config(text="Cancelled. Press SPACE to see scramble", fg="#ffff00")
        else:
            self.root.quit()
    
    def new_scramble(self):
        self.current_scramble = generate_scramble()
        self.scramble_label.config(text=self.current_scramble)

    def ask_show_times(self, solve_time):
        response = messagebox.askyesno("Solve Complete!", 
                                       f"Solve Time: {self.format_time(solve_time)}\n\nView your times?")
        if response:
            self.view_times()
    
    def update_timer(self):
        if self.running:
            self.elapsed_time = int((time.perf_counter() - self.start_time) * 1000)
            self.timer_label.config(text=self.format_time(self.elapsed_time))
        
        if self.phase == "inspection":
            elapsed = int((time.perf_counter() - self.inspection_start) * 1000)
            remaining = self.inspection_time - elapsed
            if remaining > 0:
                self.timer_label.config(text=self.format_time(remaining), fg="#ffaa00")
            else:
                self.phase = "grace"
                self.inspection_start = time.perf_counter()
                self.status_label.config(text="READY: 3 seconds", fg="#0099ff")
        
        elif self.phase == "grace":
            elapsed = int((time.perf_counter() - self.inspection_start) * 1000)
            remaining = self.grace_time - elapsed
            if remaining > 0:
                self.timer_label.config(text=self.format_time(remaining), fg="#0099ff")
            else:
                self.phase = "ready"
                self.timer_label.config(text="00:00.00", fg="#00ff00")
                self.status_label.config(text="PRESS SPACE TO START SOLVING", fg="#ff0000")
        
        elif self.phase == "ready":
            self.timer_label.config(text="00:00.00", fg="#00ff00")
        
        elif self.phase == "idle" and not self.running:
            self.timer_label.config(text="00:00.00", fg="#00ff00")
        
        self.root.after(10, self.update_timer)
    
    def view_times(self):
        if not self.times_list:
            messagebox.showinfo("Times", "No times recorded yet!")
            return
        
        if self.times_window is not None and self.times_window.winfo_exists():
            self.times_window.lift()
            self.times_window.focus()
            return
        
        self.times_window = tk.Toplevel(self.root)
        self.times_window.title("3x3 Solve Times")
        self.times_window.configure(bg="#1a1a1a")
        try:
            self.times_window.state("zoomed")
        except:
            self.times_window.geometry("800x600")
        
        def on_close():
            self.times_window.destroy()
            self.times_window = None
        
        self.times_window.protocol("WM_DELETE_WINDOW", on_close)
        
        title = tk.Label(self.times_window, text="Your Solve Times", 
                        font=("Arial", 18, "bold"), bg="#1a1a1a", fg="#00ff00")
        title.pack(pady=10)
        
        times_in_ms = [entry['time'] for entry in self.times_list]
        avg_time = sum(times_in_ms) / len(times_in_ms)
        best_time = min(times_in_ms)
        worst_time = max(times_in_ms)
        
        main_frame = tk.Frame(self.times_window, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        
        tk.Label(scrollable_frame, text="All Solves:", font=("Arial", 12, "bold"), 
                bg="#0a0a0a", fg="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))
        
        for i, entry in enumerate(self.times_list):
            solve_time = entry.get('time', 0)
            time_str = self.format_time(solve_time)
            date_str = entry.get('date', 'N/A')
            
            if solve_time == best_time:
                color = "#00ff00"
            elif solve_time == worst_time:
                color = "#ff0000"
            elif solve_time >= 40000:
                color = "#8B4513"
            else:
                color = "#ffff00"
            
            solve_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
            solve_frame.pack(fill=tk.X, padx=10, pady=3)
            
            solve_label = tk.Label(solve_frame, 
                                  text=f"{i+1}. {time_str} - {date_str}",
                                  font=("Arial", 11), bg="#1a1a1a", fg=color, anchor="w")
            solve_label.pack(side="left", fill=tk.X, expand=True)

            scr = entry.get('scramble', '')
            if scr:
                scr_label = tk.Label(solve_frame,
                                     text=scr,
                                     font=("Courier", 9), bg="#1a1a1a", fg="#888888", anchor="w")
                scr_label.pack(side="left", fill=tk.X, expand=True, padx=(8, 0))
            
            delete_btn = tk.Button(solve_frame, text="✕", 
                                  command=lambda idx=i: self.delete_solve(idx),
                                  font=("Arial", 10), bg="#ff4444", fg="white",
                                  padx=5, pady=0, cursor="hand2", bd=0)
            delete_btn.pack(side="right", padx=5)
    
    def delete_solve(self, index):
        if index < 0 or index >= len(self.times_list):
            return
        response = messagebox.askyesno("Delete Solve", 
                                       f"Delete solve: {self.format_time(self.times_list[index]['time'])}?")
        if response:
            del self.times_list[index]
            self.save_times()
            if self.times_window and self.times_window.winfo_exists():
                self.times_window.destroy()
                self.times_window = None
            self.view_times()
    
    def clear_times(self):
        response = messagebox.askyesno("Clear Times", 
                                       "Are you sure you want to clear all times?")
        if response:
            self.times_list = []
            self.save_times()
            messagebox.showinfo("Success", "All times cleared!")
            self.elapsed_time = 0
            self.running = False
            self.phase = "idle"
            self.scramble_label.pack_forget()
            self.new_scramble_btn.pack_forget()
            self.visualize_btn.pack_forget()
            self.status_label.config(text="Press SPACE to see scramble", fg="#ffff00")
            if self.times_window and self.times_window.winfo_exists():
                self.times_window.destroy()
                self.times_window = None
    
    def save_times(self):
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.json', text=True)
            try:
                with os.fdopen(temp_fd, 'w') as f:
                    json.dump(self.times_list, f, indent=2)
                shutil.move(temp_path, self.times_file)
            except:
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save times: {e}")
    
    def load_times(self):
        if os.path.exists(self.times_file):
            try:
                with open(self.times_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.times_list = [entry for entry in data if isinstance(entry, dict) and 'time' in entry]
                    else:
                        self.times_list = []
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Times file is corrupted. Starting fresh.")
                self.times_list = []
            except PermissionError:
                messagebox.showerror("Error", "Permission denied reading times file.")
                self.times_list = []
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load times: {e}")
                self.times_list = []
        else:
            self.times_list = []
    
    def exit_app(self, event=None):
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedCubeTimer(root)
    root.mainloop()
