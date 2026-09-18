const fs = require('fs');
const path = require('path');

const rootDir = __dirname;
const publicDir = path.join(rootDir, 'public');

if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

const allowedExts = ['.html', '.css', '.js', '.svg', '.xml', '.txt', '.ico', '.png', '.jpg', '.webp'];
const files = fs.readdirSync(rootDir);

files.forEach(f => {
  if (f.startsWith('sample_') || ['public', '.git', '.vercel', '__pycache__', 'New folder'].includes(f)) return;
  const src = path.join(rootDir, f);
  const stat = fs.statSync(src);
  if (stat.isFile()) {
    const ext = path.extname(f).toLowerCase();
    if (allowedExts.includes(ext)) {
      fs.copyFileSync(src, path.join(publicDir, f));
    }
  }
});

const jsSrcDir = path.join(rootDir, 'js');
const jsDstDir = path.join(publicDir, 'js');
if (fs.existsSync(jsSrcDir)) {
  if (!fs.existsSync(jsDstDir)) {
    fs.mkdirSync(jsDstDir, { recursive: true });
  }
  const jsFiles = fs.readdirSync(jsSrcDir);
  jsFiles.forEach(f => {
    fs.copyFileSync(path.join(jsSrcDir, f), path.join(jsDstDir, f));
  });
}

console.log('Synced all static assets to public/');
