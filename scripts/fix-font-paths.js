#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const cssFile = path.join(__dirname, '..', 'static', 'css', 'remixicon.css');
const content = fs.readFileSync(cssFile, 'utf8');

// Fix all font URLs to use ../fonts/ path
const fixed = content
  // First pass: fix URLs that start with remixicon
  .replace(/url\(['"]?remixicon/g, 'url("../fonts/remixicon')
  // Second pass: ensure all quotes are consistent
  .replace(/url\("\.\.\/fonts\/remixicon([^)]+)'\)/g, 'url("../fonts/remixicon$1")')
  // Third pass: fix any remaining URLs without path prefix
  .replace(/url\("remixicon\.(woff2?|ttf|eot|svg)/g, 'url("../fonts/remixicon.$1');

fs.writeFileSync(cssFile, fixed);
console.log('Fixed font paths in remixicon.css');