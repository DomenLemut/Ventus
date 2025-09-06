# Standard import
from string import ascii_uppercase
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import os
import json
import sys

# Project-specific imports
from serial_sender import SerialSender
from configuration import Configuration
from tkinter_clock import ClockPicker
from custom_coder import encode_message, encode_end


# Constants
SERIES = [f"{i:02}" for i in range(100)]
GROUPS = list(ascii_uppercase[:4])
PERIODS = ["3", "5", "10", "20", "30"]
BAUD_RATES = [9600, 19200, 38400, 57600, 115200]

def get_config_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(os.getenv("APPDATA"), "Ventus-App")
    else:
        base_dir = os.path.dirname(__file__)
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "config.json")

def save_config(config: Configuration):
    try:
        with open(get_config_path(), "w") as f:
            json.dump(config.to_dict(), f, indent=4)
    except Exception as e:
        print("Failed to save config:", e)

def load_config() -> Configuration:
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                return Configuration.from_dict(data)
        except Exception as e:
            print("Failed to load config:", e)
    return Configuration()

class MainApplication(tk.Tk):
    """Main GUI application for the Display Controller."""
    
    def __init__(self) -> None:
        super().__init__()
        self.title("Display Controller")
        self.configuration = load_config()
        self.serial_sender: SerialSender | None = None

        self._setup_main_frame()
        self._setup_choice_frames()
        self._setup_com_frame()
        self._setup_debug_field()
        self._setup_footer()

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
        self.series.set(self.configuration.series or SERIES[0])
        self.series.pack(fill="x")
        self.frame_choice1.grid(row=1, column=1, padx=5, pady=5)

        # Group selection
        tk.Label(self.frame_choice2, text="Group").pack(anchor="w")
        self.group = ttk.Combobox(self.frame_choice2, values=GROUPS, state="readonly")
        self.group.set(self.configuration.group or GROUPS[0])
        self.group.pack(fill="x")
        self.frame_choice2.grid(row=1, column=2, padx=5, pady=5)        

        # A = Right checkbox
        self.a_right_var = tk.BooleanVar(self.frame, value=self.configuration.a_right or False)
        tk.Checkbutton(self.frame, text="A = Right", variable=self.a_right_var)\
            .grid(row=2, column=2, padx=5, pady=5)

        # Close time picker
        self.clock2 = ClockPicker(
            self.frame,
            text="Close",
        )       
        self.clock2.grid(row=3, column=1, padx=5, pady=5)
        self.clock1 = ClockPicker(self.frame, text="Open", 
            command=lambda event: self.clock2.set_time(self.clock1.get_time() + timedelta(minutes=15)),
        )
        self.clock1.grid(row=2, column=1, padx=5, pady=5)

        if self.configuration.open_time:
           self.clock1.set_time(self.configuration.open_time)
           self.clock2.set_time(self.configuration.close_time) 
        else:
            self.clock1._on_change()


        # Period selection
        tk.Label(self.frame_choice3, text="Period").pack(anchor="w")
        self.period = ttk.Combobox(self.frame_choice3, values=PERIODS, state="readonly")
        self.period.set(PERIODS[1])
        self.period.pack(fill="x")
        self.frame_choice3.grid(row=3, column=2, padx=5, pady=5)

    def _setup_com_frame(self) -> None:
        """Create COM port selection and control buttons."""
        # Row 1: COM port
        self.row1 = tk.Frame(self.frame_choice4)
        tk.Label(self.row1, text="COM").pack(side=tk.LEFT)
        self.com_port_combo = ttk.Combobox(self.row1, values=[], state="readonly")
        self.com_port_combo.bind("<Button-1>", lambda e: self.refresh_ports())
        self.com_port_combo.pack(side=tk.LEFT, fill="x", expand=True)
        self.baud_rate_combo = ttk.Combobox(self.row1, values=BAUD_RATES, state="readonly", width=6)
        self.baud_rate_combo.set(BAUD_RATES[0])
        self.baud_rate_combo.pack(side=tk.RIGHT, padx=5)
        self.row1.pack(fill="x", pady=2)

        # Row 2: Status and buttons
        self.row2 = tk.Frame(self.frame_choice4)
        self.status_canvas = tk.Canvas(self.row2, width=16, height=16, highlightthickness=0)
        self.status_oval = self.status_canvas.create_oval(2, 2, 14, 14, fill="gray", outline="")
        self.status_canvas.pack(side=tk.LEFT, padx=6)

        self.connect_button = ttk.Button(self.row2, text="Connect", command=self.connect)
        self.connect_button.pack(side=tk.LEFT)
        self.display_button = ttk.Button(self.row2, text="Display", command=self.display)
        self.display_button.pack(side=tk.LEFT)
        self.row2.pack(fill="x", pady=2)

        self.frame_choice4.grid(row=4, column=0, columnspan=3, pady=10)

    def _setup_debug_field(self) -> None:
        """Create a debug text field at the bottom."""
        self.debug_field = tk.Text(self.frame, height=5, width=50, state="disabled", bg="#f0f0f0")
        self.debug_field.grid(row=5, column=0, columnspan=3, pady=10)

    def _setup_footer(self) -> None:
        """Create footer with version info."""
        self.footer = tk.Label(self, text="Modelarsko Društvo Ventus © 2025", font=("Arial", 8), fg="gray")
        self.footer.pack(side=tk.BOTTOM)

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
        # self.configuration.com_port = self.com_port_combo.get()

        save_config(self.configuration)

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
        if not self.com_port_combo.get():
            self.log_debug("Select a COM port first")
            return
        self.com_port = self.com_port_combo.get()
        self.configuration.period = self.period.get()
        self.serial_sender = SerialSender(
            com_port=self.com_port,
            speed=self.baud_rate_combo.get(),
            on_failure=lambda: self.sending_failed(),
            log_debug=self.log_debug
        )
        self.serial_sender.start()
        self.status_canvas.itemconfig(self.status_oval, fill="green")
        self.connect_button.config(text="Disconnect", command=self.disconnect)
        self.log_debug("Connected to " + self.com_port)
        self.com_port_combo.config(state="disabled")
        self.baud_rate_combo.config(state="disabled")

    def disconnect(self) -> None:
        """Disconnect from the serial device."""
        self.finalise_sending()
        if self.serial_sender:
            self.serial_sender.stop()
        self.status_canvas.itemconfig(self.status_oval, fill="gray")
        self.connect_button.config(text="Connect", command=self.connect)
        self.log_debug("Disconnected from " + self.com_port)
        self.com_port = None
        self.com_port_combo.config(state="enabled")
        self.baud_rate_combo.config(state="enabled")

    def send_to_device(self) -> None:
        """Send configuration data to the connected device."""
        if not self.serial_sender:
            self.log_debug("Not connected to any device.")
            return
        messages = encode_message(self.configuration)
        self.after(0, self.serial_sender.clear_queue())
        for message in messages:
            self.after(0, self.serial_sender.send, message)
        self.display_button.config(text="Finish", command=self.finalise_sending)

    def finalise_sending(self) -> None:
        self.serial_sender.clear_queue()
        self.serial_sender.send_flush(encode_end())
        self.display_button.config(text="Display", command=self.display)

    def force_end(self) -> None:
        self.serial_sender.clear_queue()
        for i in range(4):
            self.serial_sender.send_flush(encode_end())
        self.display_button.config(text="Display", command=self.display)

    def sending_failed(self) -> None:
        self.status_canvas.itemconfig(self.status_oval, fill="red")

    def refresh_ports(self) -> None:
        """Refresh the available COM ports."""
        ports = SerialSender.list_ports()
        self.com_port_combo['values'] = [p.device for p in ports]

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
