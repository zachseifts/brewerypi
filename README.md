# NodeBrewery

A node.js powered brewery monitoring application

## Requirements

 - mysql
 - node.js

## Setup

Create the mysql tables:

    CREATE TABLE temps (timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, temp FLOAT, host VARCHAR(128));

