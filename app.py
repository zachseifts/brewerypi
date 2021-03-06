#!/usr/bin/env python

from re import search
from socket import gethostbyname, gethostname
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from textwrap import dedent
from subprocess import Popen, PIPE

from requests import session as Session
from json import dumps

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
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')
        self.key = kwargs.get('key', '')
        self.beer = kwargs.get('beer', '')
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

    def as_celsius(self):
        ''' Returns the temperature as celsius.
        '''
        return self.temp_raw / 1000.0

    def as_fahrenheit(self):
        ''' Returns the temperature as fahrenheit.
        '''
        return (self.as_celsius() * 1.8) + 32

    def post_record(self):
        ''' Posts the record to the api.
        '''
        
        # Create a new session and set the headers
        session = Session()
        session.headers.update({'Content-Type': 'application/json'})
        session.headers.update({'Accept-Type': 'application/json'})
        
        # Logs the user in
        auth = {'username': self.username, 'password': self.password}
        session.post('%s/reading/user/login' % (self.server,), data=dumps(auth), verify=False)
        
        # Gets and sets the X-CSRF-Token header
        token = session.get('%s/services/session/token' % (self.server,), verify=False)
        session.headers.update({'X-CSRF-Token': token.text})
        
        # Format the data and POST to the server.
        data = {
            'type': 'reading',
            'title': self.key,
            'field_reading_value': { 'und': [{'value': self.as_fahrenheit()}]},
            'field_reading_category': { 'und': [{'value': 'temp', 'safe_value': 'temp'}]},
            'field_reading_beer': { 'und': self.beer}
        }
        session.post('%s/reading/node' % (self.server,), data=dumps(data), verify=False)
        
        # Log the user out
        session.post('%s/reading/user/logout' % (self.server,), verify=False)


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
    parser.add_argument('-u', '--username', type=str, metavar='username',
        help=u'The username for the api user')
    parser.add_argument('-p', '--password', type=str, metavar='password',
        help=u'The password for the api user')
    parser.add_argument('-k', '--key', type=str, metavar='key',
        help=u'The unique identifier for this device')
    parser.add_argument('-b', '--beer', type=str, metavar='BEERID',
        help=u'A unique identifier of a beer')
    args = parser.parse_args()
    main = TempSensorReader(path=args.device,
                            server=args.server,
                            username=args.username,
                            password=args.password,
                            key=args.key,
                            beer=args.beer)

