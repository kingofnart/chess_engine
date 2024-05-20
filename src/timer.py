import tkinter as tk
import time

class Timer():

    def __init__(self, parent_frame, bg_color, fg_color):
        self.time_remaining = 300  # initial time in seconds
        minutes, seconds = divmod(self.time_remaining, 60)
        self.timer_label = tk.Label(parent_frame, text=f"{minutes:01d}:{seconds:02d}", width=15, 
                                    height=2, bg=bg_color, fg=fg_color, font=("Arial", "20"))
        self.run = False

    def run_clock(self):
        if self.time_remaining > 0 and self.run:
            minutes, seconds = divmod(self.time_remaining, 60)
            self.timer_label.config(text=f"{minutes:01d}:{seconds:02d}")
            self.time_remaining -= 1
            # execute this code again after 1 second
            self.timer_label.after(1000, self.run_clock)
        elif self.time_remaining <= 0:
            self.run = False

    def toggle(self):
        self.run = not self.run
        if self.run:
            self.run_clock()

    def stop(self):
        self.run = False

    def reset(self):
        self.time_remaining = 300
        minutes, seconds = divmod(self.time_remaining, 60)
        self.timer_label.config(text=f"{minutes:01d}:{seconds:02d}")
        self.run = False