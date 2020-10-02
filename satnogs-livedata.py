import pandas as pd
import re
import sys

# Replace "YOUR_API_KEY_GOES_HERE" with your api key
url = 'https://db.satnogs.org/api/transmitters/?api_key=YOUR_API_KEY_GOES_HERE&format=json'

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

df = pd.read_json(url)
# All available fields/columns to display options are: 
# 'uuid' 'description' 'alive' 'type' 'uplink_low' 'uplink_high' 'uplink_drift' 
# 'downlink_low' 'downlink_high' 'downlink_drift' 'mode' 'mode_id' 'uplink_mode' 'invert' 'baud' 
# 'norad_cat_id' 'status' 'updated' 'citation' 'service' 'coordination' 'coordination_url'
selection = ['uuid', 'description', 'status', 'alive', 'type', 'uplink_low', 'uplink_high', 'updated']
df = df[selection]
data = df.head(3000)

def colorize(text):
    return re.sub('.*inactive.*|.*invalid.*', lambda m: '\x1b[0;31m{}\x1b[0m'.format(m.group()), text)
class MyStdout(object):
    def __init__(self, term=sys.stdout):
        self.term = term
    def write(self, text):
        text = colorize(text)
        self.term.write(text)
    def flush(self):
        pass

sys.stdout = MyStdout()
print(data)
print("")

active = df.status.str.count("active").sum()
inactive = df.status.str.count("inactive").sum()
invalid = df.status.str.count("invalid").sum()
print("\033[0;32mNumber of online SatNOGS: \033[0m", active)
print("\033[0;31mNumber of offline SatNOGS: \033[0m", inactive)
print("\033[0;33mNumber of invalid SatNOGS: \033[0m", invalid)
