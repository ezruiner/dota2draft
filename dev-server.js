// Simple static server for the `ui` directory (dev only)
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT ? Number(process.env.PORT) : 1430;
const ROOT = path.join(__dirname, 'ui');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.ico': 'image/x-icon',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2'
};

function safeJoin(root, target) {
  const resolved = path.join(root, target);
  if (!resolved.startsWith(root)) return root; // prevent path traversal
  return resolved;
}

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split('?')[0]);
  let relPath = urlPath.replace(/^\/+/, '');
  if (relPath === '' || relPath === '/') relPath = 'index.html';

  const filePath = safeJoin(ROOT, relPath);
  fs.stat(filePath, (err, stat) => {
    if (err) {
      // Fallback to index.html for SPA-like routes
      const indexPath = path.join(ROOT, 'index.html');
      fs.readFile(indexPath, (err2, data) => {
        if (err2) {
          res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
          res.end('Not found');
        } else {
          res.writeHead(200, { 'Content-Type': MIME['.html'] });
          res.end(data);
        }
      });
      return;
    }

    if (stat.isDirectory()) {
      const indexPath = path.join(filePath, 'index.html');
      fs.readFile(indexPath, (err2, data) => {
        if (err2) {
          res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
          res.end('Forbidden');
        } else {
          res.writeHead(200, { 'Content-Type': MIME['.html'] });
          res.end(data);
        }
      });
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    fs.readFile(filePath, (readErr, data) => {
      if (readErr) {
        res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('Server error');
        return;
      }
      res.writeHead(200, { 'Content-Type': type });
      res.end(data);
    });
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[dev-server] Serving ${ROOT} at http://127.0.0.1:${PORT}/`);
});
