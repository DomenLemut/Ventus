import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

MINUTES = [f"{m:02}" for m in range(0, 60)]
HOURS = [f"{h:02}" for h in range(24)]

class ClockPicker(tk.Frame):
    """A simple HH:MM time picker with a label."""
    def __init__(self, master=None, text="Set time", time=None, command=None, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command  # store external callback

        tk.Label(self, text=text).grid(row=0, column=0, padx=2, pady=2)

        self.hour_var = tk.StringVar()
        hour_cb = ttk.Combobox(
            self, textvariable=self.hour_var, values=HOURS, width=3, state="readonly"
        )
        hour_cb.grid(row=0, column=1)

        tk.Label(self, text=":").grid(row=0, column=2)

        self.minute_var = tk.StringVar()
        minute_cb = ttk.Combobox(
            self, textvariable=self.minute_var, values=MINUTES, width=3, state="readonly"
        )
        minute_cb.grid(row=0, column=3)

        # Bind events to update self.time automatically
        hour_cb.bind("<<ComboboxSelected>>", self._on_change)
        minute_cb.bind("<<ComboboxSelected>>", self._on_change)

        # Use provided time or default to "now rounded up"
        if time is None:
            time = datetime.now().replace(microsecond=0)
            if time.second > 0:
                time = time.replace(second=0) + timedelta(minutes=1)

        self.set_time(time)

    def _on_change(self, event=None):
        """Update internal self.time when user changes comboboxes."""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            self.time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        except ValueError:
            return  # ignore until both hour/minute are set

        # call external command if provided
        if self.command:
            self.command(event)

    def get_time(self) -> datetime:
        """Return selected time as a datetime (today’s date with chosen HH:MM)."""
        return self.time

    def get_time_str(self) -> str:
        """Return selected time as 'HH:MM' string."""
        return f"{self.hour_var.get()}:{self.minute_var.get()}"

    def set_time(self, time: datetime):
        """Set picker to given datetime (rounded to nearest 5 minutes)."""
        self.time = time
        self.hour_var.set(f"{time.hour:02}")
        self.minute_var.set(f"{time.minute:02}")

