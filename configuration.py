from datetime import datetime

class Configuration:
    """A simple configuration class to hold settings."""

    def __init__(self):
        self.series = None
        self.group = None
        self.open_time = None
        self.close_time = None
        self.period = None
        self.a_right = None

    def check_configuration(self):
        return (
            self.series is not None and
            self.group is not None and
            self.open_time is not None and
            self.close_time is not None and
            self.period is not None and
            isinstance(self.a_right, bool)
        )

    def to_dict(self):
        """Convert to a dict safe for JSON serialization."""
        return {
            "series": self.series,
            "group": self.group,
            "open_time": self.open_time.isoformat() if isinstance(self.open_time, datetime) else None,
            "close_time": self.close_time.isoformat() if isinstance(self.close_time, datetime) else None,
            "period": self.period,
            "a_right": self.a_right,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create Configuration from dict (JSON-friendly)."""
        cfg = cls()
        cfg.series = data.get("series")
        cfg.group = data.get("group")

        # Convert back datetime if stored as string
        ot = data.get("open_time")
        ct = data.get("close_time")
        if ot:
            cfg.open_time = datetime.fromisoformat(ot)
        if ct:
            cfg.close_time = datetime.fromisoformat(ct)

        cfg.period = data.get("period")
        cfg.a_right = data.get("a_right")
        return cfg
