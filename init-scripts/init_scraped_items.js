const fs = require('fs');
const path = require('path');

db = db.getSiblingDB('oxossi');

// Load JSON data from the file
const filePath = path.join('/docker-entrypoint-initdb.d', 'scraped_items.json');
const jsonData = JSON.parse(fs.readFileSync(filePath, 'utf8'));

db.scraped_items.insertMany(jsonData);
