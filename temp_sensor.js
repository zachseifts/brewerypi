/**
 * The temperature sensor
 */

var os = require('os')
var sys = require('sys')
var exec = require('child_process').exec;

/**
 * A temperature checker
 */
function checkTemp() {
  var start = Date.now();
  var command = '/opt/vc/bin/vcgencmd measure_temp';

  /**
   * Checks the temperature
   */
  function checkTemperature() {
    // Run the command and publish the output
    exec(command, function puts(error, stdout, stderr) {
      var now = Date.now();
      // Should replace with a regular expression
      var temp = parseFloat(stdout.replace('temp=', '').replace("'C", '').trim());
      var data = [now, temp, os.hostname()];
      console.log(data);
    });
  }

  setInterval(checkTemperature, 1000);
}

exports.checkTemp = checkTemp;

