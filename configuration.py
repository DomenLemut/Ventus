class Configuration:
    """A simple configuration class to hold settings."""
    def __init__(self):
        self.series = None
        self.group = None
        self.open_time = None
        self.close_time = None
        self.period = None
        self.a_right = None
        self.com_port = None

    def check_configuration(self):
        return (
            self.series is not None and
            self.group is not None and
            self.open_time is not None and
            self.close_time is not None and
            self.period is not None and
            isinstance(self.a_right, bool) and
            self.com_port is not None and bool(self.com_port)
        )