// Компилирует story.ink и собирает игру в один HTML-файл.
//   node tools/build.js
// Ошибки и предупреждения Ink выводятся в консоль; при ошибках игра не собирается.

const fs = require('fs');
const path = require('path');
const { Compiler } = require('inkjs/full');

const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'story.ink'), 'utf8');

const errors = [];
const warnings = [];
const compiler = new Compiler(source, {
  errorHandler: (message, type) => (type === 2 ? errors : warnings).push(message),
});

let story;
try {
  story = compiler.Compile();
} catch (e) {
  if (!errors.length) errors.push(String(e));
}

warnings.forEach(w => console.log('предупреждение:', w));
if (errors.length || !story) {
  errors.forEach(e => console.log('ОШИБКА:', e));
  process.exit(1);
}

const json = story.ToJson();
const runtime = fs.readFileSync(path.join(__dirname, 'node_modules/inkjs/dist/ink.js'), 'utf8');
const template = fs.readFileSync(path.join(__dirname, 'player.html'), 'utf8');

const html = template
  .replace('/*RUNTIME*/', () => runtime)
  .replace('/*STORY*/', () => JSON.stringify(json));

fs.writeFileSync(path.join(root, 'game.html'), html);
console.log(`game.html собран, ${Math.round(html.length / 1024)} КБ, предупреждений: ${warnings.length}`);
