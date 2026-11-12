// Regression guard for Sorin's static, hash-routed beta.
// Run alongside: node sorin-ci-check.js && node sorin-route-check.js
const fs = require('node:fs');
const assert = require('node:assert/strict');
const html = fs.readFileSync('index.html', 'utf8');
const routes = ['builder', 'templates', 'library', 'community', 'blog', 'premium'];
for (const route of routes) {
  assert.ok(html.includes('href="#' + route + '"'), 'Missing navigation link: ' + route);
  assert.ok(html.includes('data-route="' + route + '"'), 'Missing navigation marker: ' + route);
}
assert.match(html, /function\s+render\s*\(/, 'Missing route renderer');
assert.match(html, /renderers\s*=\s*\{[^}]*builder\s*:\s*builderPage[^}]*templates\s*:\s*templatesPage[^}]*library\s*:\s*libraryPage[^}]*community\s*:\s*communityPage[^}]*blog\s*:\s*blogPage[^}]*premium\s*:\s*premiumPage/s, 'Route table incomplete');
// Issue #2: navigating away from a template preview must close the modal.
assert.match(html, /addEventListener\s*\(\s*['"]hashchange['"]\s*,\s*\(\s*\)\s*=>\s*\{\s*closeModal\s*\(\s*\)\s*;\s*render\s*\(/, 'Navigation must close the modal before rendering');
console.log('PASS: 6 navigation routes and modal-close regression guard');
