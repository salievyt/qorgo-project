import fs from 'node:fs/promises';
import { render } from '../.prerender/entry-server.js';
const path = new URL('../dist/index.html', import.meta.url);
const html = await fs.readFile(path, 'utf8');
const markup = render();
if (!markup.includes('<h1>') || !markup.includes('QORGO_Presentation.pptx')) throw new Error('Prerender missing required content');
await fs.writeFile(path, html.replace('<div id="root"></div>', `<div id="root">${markup}</div>`));
console.log('Static HTML generated for search engines and visitors.');
