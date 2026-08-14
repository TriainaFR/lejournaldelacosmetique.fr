// Mini serveur statique pour prévisualiser la maquette (aucune dépendance).
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { join, extname, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const port = Number(process.env.PORT || 4173);

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.xml': 'application/xml; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
};

createServer(async (req, res) => {
  try {
    let path = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (path.includes('..')) { res.writeHead(400); res.end('Bad request'); return; }
    if (path.endsWith('/')) path += 'index.html';
    let file = join(root, path);
    let body;
    try {
      body = await readFile(file);
    } catch {
      // /chemin sans slash final -> /chemin/index.html
      try {
        file = join(root, path, 'index.html');
        body = await readFile(file);
      } catch {
        res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end('<!doctype html><meta charset="utf-8"><title>404</title><p style="font-family:Georgia;padding:40px">404 — page non incluse dans la maquette (pour l’instant).</p>');
        return;
      }
    }
    res.writeHead(200, { 'Content-Type': mime[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(body);
  } catch (e) {
    res.writeHead(500); res.end('Erreur serveur');
  }
}).listen(port, '127.0.0.1', () => {
  console.log(`Maquette servie sur http://127.0.0.1:${port}`);
});
