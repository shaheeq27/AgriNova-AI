const { chromium } = require('playwright-core');

(async () => {
  const browser = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const context = await browser.newContext();
  
  // Set auth token to bypass login guard
  await context.addInitScript(() => {
    window.localStorage.setItem('agrinova_token', 'dummy_token');
  });

  const page = await context.newPage();
  
  await page.goto('http://localhost:3000/home', { waitUntil: 'networkidle' });
  await page.setViewportSize({ width: 1440, height: 900 });
  
  await page.screenshot({ path: '/Users/shaheeq.s/.gemini/antigravity/brain/e41ed62e-1e22-43c0-bd53-e33f063c18f7/home_new_hero.png' });
  
  await browser.close();
  console.log("Screenshot saved to home_new_hero.png in artifacts directory.");
})();
