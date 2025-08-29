from configuration import Configuration
from custom_coder import encode_message

config = Configuration()
config.series = "12"
config.group = "A"
config.open_time = "08:30"
config.close_time = "17:45"
config.a_right = True
messages = encode_message(config)
for msg in messages:
    print(msg)