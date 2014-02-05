# Raspberry Pi Brewery

This project is a brew system for a raspberry pi and a few other peices of hardware. Right now it logs temperatures from a DS18B20 sensor and posts to a Drupal based webapp. Soon it will allow the raspberry pi to control fermentation temperatures.

## Requirements

 - Python
 - Raspberry pi
 - DS18B20 Digital temperature sensor

## Usage

    ./app.py -d /path/to/the/device -s http://rest.server.com/temp -u username -p password -k device_name

