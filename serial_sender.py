import threading
import queue
import serial
import serial.tools.list_ports
import time
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

class SerialSender:
    def __init__(self, com_port, period, speed, on_failure=None, log_debug=None):
        self.com_port = com_port
        self.period = int(period)
        self.speed = speed
        self.running = False
        self.messages = []
        self.thread = None
        self.ser = None

        # Callbacks
        self.log_debug = log_debug if log_debug else logging.debug
        self.on_failure = on_failure if on_failure else lambda: None

    def start(self):
        """Start background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.log_debug(f"SerialSender started on {self.com_port} at {self.speed} baud")

    def stop(self):
        """Stop background thread and close port."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                self.log_debug("Serial port closed")
            except Exception as e:
                logging.error(f"Error closing serial port: {e}")

    def send(self, message):
        """Add a message to the list (delayed by period)."""
        self.messages.append(message)

    def send_flush(self, message):
        """Add a message to the list immediately (ignores pacing)."""
        self.messages.append(message)

    def clear_queue(self):
        """Clear all pending messages."""
        self.messages.clear()

    def _run(self):
        """Worker thread: open port, send messages, and read responses."""
        try:
            self.ser = serial.Serial(self.com_port, self.speed, timeout=1)
        except Exception as e:
            logging.error(f"Failed to open {self.com_port}: {e}")
            self.on_failure()
            return

        with self.ser:
            last_send_time = 0
            while self.running:
                # --- Read incoming data ---
                try:
                    if self.ser.in_waiting > 0:
                        response = self.ser.readline().decode(errors="replace").strip()
                        if response:
                            self.log_debug(f"Received: {response}")
                except Exception as e:
                    logging.error(f"Read error: {e}")
                    self.on_failure()
                    break

                # --- Send outgoing messages ---
                if self.messages and (time.time() - last_send_time) >= self.period:
                    msg = self.messages.pop(0)  # send one at a time
                    try:
                        self.ser.write(msg.encode() + b"\r\n")
                        self.log_debug(f"Sent: {msg}")
                    except Exception as e:
                        logging.error(f"Serial write error: {e}")
                        self.on_failure()
                        break
                    last_send_time = time.time()

                time.sleep(0.05)  # prevent busy-loop

            self.log_debug("SerialSender thread exited")


    @staticmethod
    def list_ports():
        """Helper to list available COM ports."""
        return serial.tools.list_ports.comports()
