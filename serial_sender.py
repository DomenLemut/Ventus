import threading
import queue
import serial
import serial.tools.list_ports
import time
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

class SerialSender:
    def __init__(self, com_port, period, speed, on_done=None, on_failure=None, log_debug=None):
        self.com_port = com_port
        self.period = int(period)
        self.speed = speed
        self.running = False
        self.msg_queue = queue.Queue()
        self.thread = None
        self.ser = None

        # Callbacks
        self.log_debug = log_debug if log_debug else logging.debug
        self.on_done = on_done if on_done else lambda: None
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
        """Queue a message (delayed by period)."""
        self.msg_queue.put(message)
        # don’t sleep here, handle pacing in _run

    def send_flush(self, message):
        """Queue a message immediately (ignores pacing)."""
        self.msg_queue.put_nowait(message)

    def clear_queue(self):
        """Clear all pending messages."""
        with self.msg_queue.mutex:
            self.msg_queue.queue.clear()

    def _run(self):
        """Worker thread: open port, send messages, handle errors."""
        try:
            self.ser = serial.Serial(self.com_port, self.speed, timeout=1)
        except Exception as e:
            logging.error(f"Failed to open {self.com_port}: {e}")
            self.on_failure()
            return

        sent_anything = False

        with self.ser:
            while self.running:
                try:
                    msg = self.msg_queue.get(timeout=0.5)
                    if self.ser.is_open:
                        self.ser.write(msg.encode() + b"\r\n")
                        self.log_debug(f"Sent: {msg}")
                        sent_anything = True
                        time.sleep(self.period)  # pacing here
                    else:
                        raise serial.SerialException("Port closed unexpectedly")
                except queue.Empty:
                    # only call on_done if we actually sent something before
                    if sent_anything:
                        self.on_done()
                        sent_anything = False
                    continue
                except Exception as e:
                    logging.error(f"Serial error: {e}")
                    self.on_failure()
                    break

        self.running = False
        self.log_debug("SerialSender thread exited")


    @staticmethod
    def list_ports():
        """Helper to list available COM ports."""
        return serial.tools.list_ports.comports()
