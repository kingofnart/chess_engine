import tkinter as tk
import time

class Timer():

    def __init__(self, parent_frame):
        self.sec = 0
        self.min = 5
        self.timer_label = tk.Label(parent_frame, text=f"{self.min:01d}:{self.sec:02d}", width=7, height=2, bg="#00a305")
        self.time_remaining = 300  # 5 min
        self.has_time = True
        self.run = False

    def run_clock(self):
        self.time_remaining = int(self.min)*60 + int(self.sec)
        while self.time_remaining > 0 and self.run:
            minutes, seconds = divmod(self.time_remaining, 60)
            self.timer_label.config(text=f"{minutes:01d}:{seconds:02d}")
            self.time_remaining -= 1
        self.has_time = False

    def toggle(self):
        self.run = not self.run
        if self.run:
            self.run_clock()