// Прогон истории в консоли: ошибки, порядок сцен, число строк, время чтения.
//   node tools/play.js
const fs = require('fs');
const path = require('path');
const { Compiler } = require('inkjs/full');
const src = fs.readFileSync(path.join(__dirname, '..', 'story.ink'), 'utf8');
const issues = [];
const st = new Compiler(src, { errorHandler: (m, t) => issues.push(m) }).Compile();
console.log('ошибок и предупреждений:', issues.length, issues.join('\n'));
let lines = 0, todo = 0, words = 0;
while (st.canContinue) {
  const l = st.Continue().trim();
  const scene = st.currentTags.find(t => t.startsWith('scene:'));
  if (scene) console.log('\n== ' + scene.slice(6).trim() + ' ==');
  if (!l) continue;
  lines++;
  if (l.startsWith('[TODO')) todo++; else words += l.split(/\s+/).length;
  console.log('  ' + l);
}
console.log(`\nстрок: ${lines}, заглушек TODO: ${todo}, слов текста: ${words}, ~${Math.round(words / 160)} мин чтения`);
console.log('история дошла до конца:', !st.canContinue && !st.currentChoices.length);
