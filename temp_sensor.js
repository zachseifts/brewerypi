/**
 * The temperature sensor
 */

var os = require('os')
var exec = require('child_process').exec;
var mysql = require('mysql');

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
      var now = Math.round(Date.now() / 1000);
      // Should replace with a regular expression
      var temp = parseFloat(stdout.replace('temp=', '').replace("'C", '').trim());
      var data = {
        'temp': temp,
        'hostname': os.hostname()
      };

      // Connect to the mysql server
      var conn = mysql.createConnection({
        host: 'localhost',
        database: 'brewery',
        user: 'root',
        password: 'root'
      });
      conn.connect();

      // Create the record
      var query = conn.query('INSERT INTO temps SET ?', data, function(err, result) {
        if (err) {
          console.log('error!' + err);
        };
      });

      // Close the connection
      conn.end();
    });
  }

  console.log('Starting temp sensor');
  checkTemperature();
  // Run checkTemperature() every 60 seconds
  setInterval(checkTemperature, 1000 * 60);
}

exports.checkTemp = checkTemp;

