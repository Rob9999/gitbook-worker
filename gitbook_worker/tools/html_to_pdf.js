#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

async function htmlToPdf(inputPath, outputPath) {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  const fileUrl = 'file://' + path.resolve(inputPath);
  await page.goto(fileUrl, { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'screen' });
  await page.pdf({
    path: outputPath,
    printBackground: true,
    preferCSSPageSize: true,
    format: 'A4',
    margin: { top: '12mm', bottom: '12mm', left: '15mm', right: '15mm' },
  });
  await browser.close();
}

async function main() {
  const [, , inputPath, outputPath] = process.argv;
  if (!inputPath || !outputPath) {
    console.error('Usage: node html_to_pdf.js <input.html> <output.pdf>');
    process.exit(1);
  }
  if (!fs.existsSync(inputPath)) {
    console.error(`Input file not found: ${inputPath}`);
    process.exit(2);
  }
  const outDir = path.dirname(path.resolve(outputPath));
  fs.mkdirSync(outDir, { recursive: true });
  try {
    await htmlToPdf(inputPath, outputPath);
  } catch (error) {
    console.error('Failed to render PDF:', error);
    process.exit(3);
  }
}

main();
