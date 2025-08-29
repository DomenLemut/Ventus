# Standard import
from string import ascii_uppercase
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import time

# Project-specific imports
from serial_sender import SerialSender
from configuration import Configuration
from tkinter_clock import ClockPicker
from custom_coder import encode_message, encode_end, enclode_force_stop
import json

# Constants
SERIES = [f"{i:02}" for i in range(100)]
GROUPS = list(ascii_uppercase[:4])
PERIODS = ["3", "5", "10", "20", "30"]

class MainApplication(tk.Tk):
    """Main GUI application for the Display Controller."""
    
    def __init__(self) -> None:
        super().__init__()
        self.title("Display Controller")
        self.configuration = Configuration()
        self.serial_sender: SerialSender | None = None

        self._setup_main_frame()
        self._setup_choice_frames()
        self._setup_com_frame()
        self._setup_debug_field()

    # -------------------- UI Setup -------------------- #
    def _setup_main_frame(self) -> None:
        self.frame = tk.Frame(self, width=300, height=200)
        self.frame.pack(pady=20, padx=20)

    def _setup_choice_frames(self) -> None:
        """Create frames and widgets for user choices."""
        # Frames
        self.frame_choice1 = tk.Frame(self.frame)
        self.frame_choice2 = tk.Frame(self.frame)
        self.frame_choice3 = tk.Frame(self.frame)
        self.frame_choice4 = tk.Frame(self.frame)

        # Series selection
        tk.Label(self.frame_choice1, text="Series").pack(anchor="w")
        self.series = ttk.Combobox(self.frame_choice1, values=SERIES, state="readonly")
        self.series.set(SERIES[0])
        self.series.pack(fill="x")
        self.frame_choice1.grid(row=1, column=1, padx=5, pady=5)

        # Group selection
        tk.Label(self.frame_choice2, text="Group").pack(anchor="w")
        self.group = ttk.Combobox(self.frame_choice2, values=GROUPS, state="readonly")
        self.group.set(GROUPS[0])
        self.group.pack(fill="x")
        self.frame_choice2.grid(row=1, column=2, padx=5, pady=5)        

        # A = Right checkbox
        self.a_right_var = tk.BooleanVar()
        tk.Checkbutton(self.frame, text="A = Right", variable=self.a_right_var)\
            .grid(row=2, column=2, padx=5, pady=5)

        # Close time picker
        self.clock2 = ClockPicker(
            self.frame,
            text="Close"
        )       
        self.clock2.grid(row=3, column=1, padx=5, pady=5)
        self.clock1 = ClockPicker(self.frame, text="Open", 
            command=lambda event: self.clock2.set_time(self.clock1.get_time() + timedelta(minutes=15))
        )
        self.clock1.grid(row=2, column=1, padx=5, pady=5)
        self.clock1._on_change()

        # Period selection
        tk.Label(self.frame_choice3, text="Period").pack(anchor="w")
        self.period = ttk.Combobox(self.frame_choice3, values=PERIODS, state="readonly")
        self.period.set(PERIODS[1])
        self.period.pack(fill="x")
        self.frame_choice3.grid(row=3, column=2, padx=5, pady=5)

    def validate_close_time(event=None):
        if self.clock2.get_time() <= self.clock1.get_time():
            self.log_debug("Closing time must be later than opening time!")

    def _setup_com_frame(self) -> None:
        """Create COM port selection and control buttons."""
        # Row 1: COM port
        self.row1 = tk.Frame(self.frame_choice4)
        tk.Label(self.row1, text="COM").pack(side=tk.LEFT)
        self.com_port_combo = ttk.Combobox(self.row1, values=[], state="readonly")
        self.com_port_combo.bind("<Button-1>", lambda e: self.refresh_ports())
        self.com_port_combo.pack(side=tk.LEFT, fill="x", expand=True)
        self.row1.pack(fill="x", pady=2)

        # Row 2: Status and buttons
        self.row2 = tk.Frame(self.frame_choice4)
        self.status_canvas = tk.Canvas(self.row2, width=16, height=16, highlightthickness=0)
        self.status_oval = self.status_canvas.create_oval(2, 2, 14, 14, fill="gray", outline="")
        self.status_canvas.pack(side=tk.LEFT, padx=6)

        self.connect_button = ttk.Button(self.row2, text="Connect", command=self.connect)
        self.connect_button.pack(side=tk.LEFT)
        self.display_button = ttk.Button(self.row2, text="Display", command=self.display)
        self.display_button.pack(side=tk.RIGHT)
        self.row2.pack(fill="x", pady=2)

        self.frame_choice4.grid(row=4, column=0, columnspan=3, pady=10)

    def _setup_debug_field(self) -> None:
        """Create a debug text field at the bottom."""
        self.debug_field = tk.Text(self.frame, height=5, width=50, state="disabled", bg="#f0f0f0")
        self.debug_field.grid(row=5, column=0, columnspan=3, pady=10)

    def log_debug(self, message: str) -> None:
        """Append a line to the debug field and trim to last 4 lines."""
        self.debug_field.config(state="normal")
        self.debug_field.insert("end", message + "\n")
        self.debug_field.see("end")

        lines = self.debug_field.get("1.0", "end-1c").splitlines()
        if len(lines) > 4:
            self.debug_field.delete("1.0", "end")
            self.debug_field.insert("end", "\n".join(lines[-4:]) + "\n")
        self.debug_field.config(state="disabled")

    def get_configuration(self) -> None:
        self.configuration.series = self.series.get()
        self.configuration.group = self.group.get()
        self.configuration.open_time = self.clock1.get_time()
        self.configuration.close_time = self.clock2.get_time()
        self.configuration.period = self.period.get()
        self.configuration.a_right = self.a_right_var.get()
        self.configuration.com_port = self.com_port_combo.get()

    def display(self) -> None:
        """Gather configuration and send to device if valid."""
        self.get_configuration()

        if self.configuration.check_configuration():
            # print(json.dumps(self.configuration.__dict__, default=str, indent=2))
            self.send_to_device()
        else:
            self.log_debug("Configuration is incomplete or invalid")

    def connect(self) -> None:
        """Connect to the serial device."""
        self.configuration.com_port = self.com_port_combo.get()
        self.configuration.period = self.period.get()
        self.serial_sender = SerialSender(
            com_port=self.configuration.com_port,
            period=self.configuration.period,
            speed=115200,
            on_done=lambda: self.everything_has_been_sent(),
            on_failure=lambda: self.sending_failed(),
            log_debug=self.log_debug
        )
        self.serial_sender.start()
        self.status_canvas.itemconfig(self.status_oval, fill="green")
        self.connect_button.config(text="Disconnect", command=self.disconnect)
        self.log_debug("Connected to " + self.configuration.com_port)

    def disconnect(self) -> None:
        """Disconnect from the serial device."""
        self.serial_sender.send(encode_end())
        if self.serial_sender:
            self.serial_sender.stop()
        self.status_canvas.itemconfig(self.status_oval, fill="gray")
        self.connect_button.config(text="Connect", command=self.connect)

    def send_to_device(self) -> None:
        """Send configuration data to the connected device."""
        if not self.serial_sender:
            self.log_debug("Not connected to any device.")
            return
        messages = encode_message(self.configuration)
        for message in messages:
            self.after(0, self.serial_sender.send, message)
        self.display_button.config(text="Stop", command=self.force_end)
    
    def everything_has_been_sent(self) -> None:
        """Callback when all messages have been sent."""
        self.display_button.config(text="Display", command=self.display)

    def force_end(self) -> None:
        for i in range(4    ):
            self.serial_sender.send(encode_end())
        self.display_button.config(text="Display", command=self.display)

    def sending_failed(self) -> None:
        self.status_canvas.itemconfig(self.status_oval, fill="red")

    def refresh_ports(self) -> None:
        """Refresh the available COM ports."""
        ports = serial.tools.list_ports.comports()
        self.com_port_combo['values'] = [p.device for p in ports]

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
