#!/usr/bin/env python

import sys
import sqlite3
import re
import socket
import subprocess
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from textwrap import dedent

class BadTemperatureReading(Exception): pass
class BadSqlite3(Exception): pass

class TempSensorReader(object):
    ''' Processes the data from the sensor and converts it to C and F.
    
    Mostly copied from Adafruit's Raspberry Pi DS18B20 tutorial. This takes the
    output from the sensor, typically from /sys/bus/w1/devices/ and converts it
    to the proper temperature.
    '''

    def __init__(self, **kwargs):
        self.device_file = kwargs.get('path', '')
        self.database = kwargs.get('database', '')
        self.ip = socket.gethostbyname(socket.gethostname())
        self.read_temp()
        self.write_record()

    def read_temp(self):
        ''' Converts the raw data to a human redable format.
        '''
        catdata = subprocess.Popen(
            ['cat', self.device_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = catdata.communicate()

        if err:
            raise BadTemperatureReading, 'Bad temperature from file'

        data = out.decode('utf-8').split('\n')

        if not re.search('YES', data[0]):
            raise BadTemperatureReading, 'Invalid data from sensor'
        
        self.temp_raw = int(re.search(r"t=\d+", data[1]).group(0).lstrip('t='))

    def write_record(self):
        ''' Writes the temperature the a sqlite database.
        '''
        con = '';
        try:
            con = sqlite3.connect(self.database)
            cur = con.cursor()
            create_sql = '''
            CREATE TABLE IF NOT EXISTS brewery
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
               created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               temp INTEGER NOT NULL,
               ip TEXT NOT NULL
              )
            '''
            cur.execute(create_sql)
            cur.execute("INSERT INTO brewery(temp,ip) VALUES (?,?)", (self.temp_raw, self.ip))
            con.commit();
        except sqlite3.Error, e:
            raise BadSqlite3, e
            sys.exit(1)
        finally:
            if con:
                con.close()


if __name__ == '__main__':
    description = dedent('''\
    Logs the temperature from a rasperry pi based logger thing.
    ''')
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
        description=description)
    parser.add_argument('-p', '--path', type=str, metavar='/path/to/device/',
        help=u'The file system path to the device')
    parser.add_argument('-d', '--database', type=str, metavar='/path/to/database.sqlite',
        help=u'The file system path to the database')
    args = parser.parse_args()
    main = TempSensorReader(path=args.path, database=args.database)

