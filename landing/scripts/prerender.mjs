import fs from 'node:fs/promises';
import { render } from '../.prerender/entry-server.js';
const path = new URL('../dist/index.html', import.meta.url);
let html = await fs.readFile(path, 'utf8');
// Small site stylesheet: inline at build time to remove a render-blocking round trip.
const stylesheet = html.match(/<link rel="stylesheet"[^>]*href="([^"]+)"[^>]*>/);
if (!stylesheet) throw new Error('Missing built stylesheet');
const css = await fs.readFile(new URL('../dist' + stylesheet[1], import.meta.url), 'utf8');
if (css.includes('@import')) throw new Error('External CSS imports delay first paint');
html = html.replace(stylesheet[0], `<style>${css}</style>`);
const markup = render();
if (!markup.includes('<h1>') || !markup.includes('QORGO_Presentation.pptx')) throw new Error('Prerender missing required content');
await fs.writeFile(path, html.replace('<div id="root"></div>', `<div id="root">${markup}</div>`));
console.log('Static HTML generated for search engines and visitors.');
