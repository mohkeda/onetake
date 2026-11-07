import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'child_process';
const FPS = 30;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + process.argv[2]); await p.evaluate(() => document.fonts.ready);
const total = await p.evaluate(() => window.TOTAL);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '18', '-movflags', '+faststart', process.argv[3]], { stdio: ['pipe', 'inherit', 'inherit'] });
const n = Math.round(total * FPS);
for (let i = 0; i <= n; i++) {
  await p.evaluate(t => render(t), i / FPS);
  const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
console.log('frames', n + 1);
