import threading
import queue
import serial
import time

class SerialSender:
    def __init__(self, com_port, period, speed, on_done=None, on_failure=None, log_debug=None):
        self.com_port = com_port
        self.period = int(period)
        self.running = False
        self.speed = speed
        self.msg_queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)

        self.log_debug = log_debug if log_debug else lambda msg: None
        self.on_done = on_done if on_done else lambda: None
        self.on_failure = on_failure if on_failure else lambda: None

    def start(self):
        self.running = True
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self):
        self.running = False

    def send(self, message):
        """Add a message to the queue."""
        self.msg_queue.put(message)
        time.sleep(self.period)

    def _run(self):
        try:
            # Try to open serial port once
            ser = serial.Serial(self.com_port, self.speed, timeout=1)
        except Exception as e:
            print("Serial open error:", e)
            self.on_failure()
            return  # Exit thread if cannot open

        # Keep the port open inside a context manager
        with ser:
            while self.running:
                try:
                    msg = self.msg_queue.get(timeout=0.5)
                    #self.log_debug(msg)
                    if ser.is_open:
                        ser.write(msg.encode() + b'\r\n')
                    else:
                        raise serial.SerialException("Port closed unexpectedly")
                except queue.Empty:
                    # no messages left → signal done
                    continue
                except Exception as e:
                    print("Serial error:", e)
                    self.on_failure()
                    break  # exit loop if error
