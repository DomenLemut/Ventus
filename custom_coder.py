
"""
2. Na COM port se v ASCII formatu periodično pošiljajo nizi po vrsti na vsakih Period sekund ('_' pomeni presledek). Vsak niz se začne z '#', da ga tabla lahko loči od drugih sporočil, ki jih podpira zdaj:

    - Serija in skupina kot "#ss__g_", kjer je "ss" serija (dva znaka 0 do 99) in "g" skupina (en znak A do C)

    - Odpiranje kot "#O_mm_mm", kjer je "hh" ura in "mm" minuta

    - Zapiranje kot "#C_mm_mm", kjer je "hh" ura in "mm" minuta


hash + 6 znakov + /r + /n
"""
from configuration import Configuration

def encode_message(config: Configuration) -> list[str]:
    """Encode the configuration into a list of messages to send."""
    messages = []
    
    # Series and Group
    series = config.series.zfill(2) if config.series else "00"
    group = config.group if config.group else " "
    messages.append(f"#{series}  {group} ")
    
    # Open Time
    if config.open_time:
        open_hour = config.open_time.hour
        open_minute = config.open_time.minute
        messages.append(f"#O {open_hour} {open_minute}")
    
    # Close Time
    if config.close_time:
        close_hour = config.close_time.hour
        close_minute = config.close_time.minute
        messages.append(f"#C {close_hour} {close_minute}")

    if config.a_right is not None:
        if config.a_right:
            messages.append(f"#RIGHT  ")
        else:
            messages.append(f"#LEFT   ")
    
    return messages

def encode_end() -> str:
    return "#        "

def enclode_force_stop() -> list[str]:
    return [encode_end(), encode_end(), encode_end(), encode_end()]

