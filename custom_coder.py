
"""
2. Na COM port se v ASCII formatu periodično pošiljajo nizi po vrsti na vsakih Period sekund ('_' pomeni presledek). Vsak niz se začne z '#', da ga tabla lahko loči od drugih sporočil, ki jih podpira zdaj:

    - Serija in skupina kot "#ss__g_", kjer je "ss" serija (dva znaka 0 do 99) in "g" skupina (en znak A do C)

    - Odpiranje kot "#O_mm_mm", kjer je "hh" ura in "mm" minuta

    - Zapiranje kot "#C_mm_mm", kjer je "hh" ura in "mm" minuta


hash + 6 znakov + /r + /n
"""
from configuration import Configuration
from datetime import time

def encode_clock(datetime: time) -> str:
    """Encode a datetime object into a time string."""
    open_hour = datetime.hour
    open_minute = datetime.minute
    open_hour_str = f"{open_hour:02}"
    open_minute_str = f"{open_minute:02}"
    return f"{open_hour_str}:{open_minute_str}"

def encode_message(config: Configuration) -> list[str]:
    """Encode the configuration into a list of messages to send."""
    messages = []
    
    # Series and Group
    series = config.series.zfill(2) if config.series else "00"
    group = config.group if config.group else " "
    messages.append(f"#{series}  {group} ")
    
    # Open Time
    if config.open_time:
        messages.append(f"#O {encode_clock(config.open_time)}")
    
    # Close Time
    if config.close_time:
        messages.append(f"#C {encode_clock(config.close_time)}")

    if config.a_right is not None:
        if config.a_right and config.group in ['A', 'C'] or \
        not config.a_right and config.group in ['B', 'D']:
            messages.append(f"#RIGHT  ")
        else:
            messages.append(f"#LEFT   ")
    
    return messages

def encode_end() -> str:
    return "#        "