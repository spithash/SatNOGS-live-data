#!/usr/bin/env python3

import pandas as pd
import re
import sys
import configparser
import time
import signal


def signal_handler(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

while True:
    # Process commandline options and parse configuration
    cfg = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    cfg.read('configuration.ini')

    SATNOGS_DB_API_KEY = cfg.get('Credentials', 'SATNOGS_DB_API_KEY')

    url = 'https://db.satnogs.org/api/transmitters/?api_key={}&format=json'.format(SATNOGS_DB_API_KEY)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    df = pd.read_json(url)
    # All available fields/columns of the 'transmitters' API are:
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

    from pandas_streaming.df import StreamingDataFrame

    sdf = StreamingDataFrame.read_df(data)

    for data in sdf:
        print(data)
        print("")
        active = df.status.str.count("active").sum()
        inactive = df.status.str.count("inactive").sum()
        invalid = df.status.str.count("invalid").sum()
        print("\033[0;32mNumber of active SatNOGS: \033[0m", active)
        print("\033[0;31mNumber of inactive SatNOGS: \033[0m", inactive)
        print("\033[0;33mNumber of invalid SatNOGS: \033[0m", invalid)

    for remaining in range(300, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("Refreshing in {:2d} seconds...".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
pass
