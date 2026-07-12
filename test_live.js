const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

  const url = 'https://zsm-record.vercel.app';
  console.log('Loading:', url);
  
  await page.goto(url, { waitUntil: 'networkidle0' });
  await page.screenshot({path: 'pup_live_screenshot.png'});

  await browser.close();
})();
