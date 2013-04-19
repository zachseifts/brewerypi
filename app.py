#!/usr/bin/env python

from re import search
from socket import gethostbyname, gethostname
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from textwrap import dedent
from subprocess import Popen, PIPE

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
        self.server = kwargs.get('server', '')
        self.creds = kwargs.get('creds', '')
        self.key = kwargs.get('key', '')
        self.ip = gethostbyname(gethostname())
        self.read_temp()
        self.post_record()

    def read_temp(self):
        ''' Converts the raw data to a human redable format.
        '''
        catdata = Popen(
            ['cat', self.device_file],
            stdout=PIPE,
            stderr=PIPE
        )
        out, err = catdata.communicate()

        if err:
            raise BadTemperatureReading, 'Bad temperature from file'

        data = out.decode('utf-8').split('\n')

        if not search(r'YES', data[0]):
            raise BadTemperatureReading, 'Invalid data from sensor'
        
        self.temp_raw = int(search(r't=\d+', data[1]).group(0).lstrip('t='))

    def post_record(self):
        ''' Posts the record to the api.
        '''
        request = Popen(
            ['curl',
             '-X', 'POST',
             '--user', self.creds,
             '%s/%s/%d' % (self.server, self.key, self.temp_raw)],
            stdout=PIPE,
            stderr=PIPE)

if __name__ == '__main__':
    description = dedent('''\
    Logs the temperature from a rasperry pi based logger thing.
    ''')
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
        description=description)
    parser.add_argument('-d', '--device', type=str, metavar='/path/to/device/',
        help=u'The file system path to the device')
    parser.add_argument('-s', '--server', type=str, metavar='http://rest.api.su/temps/',
        help=u'The url for the rest server')
    parser.add_argument('-c', '--creds', type=str, metavar='username:password',
        help=u'The credentials for the rest api')
    parser.add_argument('-k', '--key', type=str, metavar='key',
        help=u'The unique identifier for this device')
    args = parser.parse_args()
    main = TempSensorReader(path=args.device,
                            server=args.server,
                            creds=args.creds,
                            key=args.key)

