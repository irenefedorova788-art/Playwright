// Снимает страницу целиком, сохраняя настоящий размер окна.
//
//   node tools/shot.js <файл.html> <результат.png> [ширина] [высота]
//
// Обычный headless-скриншот снимает ровно окно: блок высотой в экран
// растягивается на всю страницу и кадр разъезжается. Здесь окно остаётся
// нормальным, а снимок делается за его пределы — через протокол Chrome.

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const PORT = 9333;

const [file, out, width = '1200', height = '900'] = process.argv.slice(2);
if (!file || !out) {
  console.error('Нужны исходник и результат: shot.js <html> <png> [ширина] [высота]');
  process.exit(1);
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function target() {
  // Chrome поднимается не мгновенно — ждём, пока отзовётся отладочный порт.
  for (let attempt = 0; attempt < 50; attempt++) {
    try {
      const list = await fetch(`http://127.0.0.1:${PORT}/json/list`).then(r => r.json());
      const page = list.find(t => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(200);
  }
  throw new Error('Chrome не отозвался на отладочном порту');
}

(async () => {
  const chrome = spawn(CHROME, [
    '--headless', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
    `--remote-debugging-port=${PORT}`,
    `--window-size=${width},${height}`,
    'about:blank',
  ], { stdio: 'ignore' });

  try {
    const socket = new WebSocket(await target());
    await new Promise(r => socket.addEventListener('open', r, { once: true }));

    let id = 0;
    const pending = new Map();
    socket.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (pending.has(message.id)) {
        pending.get(message.id)(message.result);
        pending.delete(message.id);
      }
    });

    const send = (method, params = {}) => new Promise(resolve => {
      const messageId = ++id;
      pending.set(messageId, resolve);
      socket.send(JSON.stringify({ id: messageId, method, params }));
    });

    await send('Page.enable');
    await send('Page.navigate', { url: 'file://' + path.resolve(file) });
    await sleep(1200); // вёрстка и шрифты

    const { contentSize } = await send('Page.getLayoutMetrics');
    const shot = await send('Page.captureScreenshot', {
      format: 'png',
      captureBeyondViewport: true,
      clip: {
        x: 0, y: 0,
        width: Math.ceil(contentSize.width),
        height: Math.ceil(contentSize.height),
        scale: 1,
      },
    });

    fs.writeFileSync(out, Buffer.from(shot.data, 'base64'));
    console.log(`  снято ${Math.ceil(contentSize.width)}×${Math.ceil(contentSize.height)} → ${out}`);
    socket.close();
  } finally {
    chrome.kill();
  }
})();
