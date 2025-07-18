#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const cssFile = path.join(__dirname, '..', 'static', 'css', 'remixicon.css');
const content = fs.readFileSync(cssFile, 'utf8');

const fixed = content
  .replace(/url\(['"]remixicon/g, 'url("../fonts/remixicon')
  .replace(/url\("\.\.\/fonts\/remixicon([^)]+)'\)/g, 'url("../fonts/remixicon$1")');

fs.writeFileSync(cssFile, fixed);
console.log('Fixed font paths in remixicon.css');