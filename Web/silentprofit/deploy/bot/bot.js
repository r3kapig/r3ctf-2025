const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
app.use(express.urlencoded({ extended: false }));


const flag = process.env['FLAG'] ?? 'flag{test_flag}';
const PORT = process.env?.BOT_PORT || 31337;

app.post('/report', async (req, res) => {
  const { url } = req.body;

  if (!url || !url.startsWith('http://localhost/')) {
    return res.status(400).send('Invalid URL');
  }

  try {
    console.log(`[+] Visiting: ${url}`);
    const browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
      ]
    });

    await browser.setCookie({ name: 'flag', value: flag, domain: 'localhost' });
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 5000 });
    await page.waitForNetworkIdle({timeout: 5000})
    await browser.close();
    res.send('URL visited by bot!');
  } catch (err) {
    console.error(`[!] Error visiting URL:`, err);
    res.status(500).send('Bot error visiting URL');
  }
});

app.get('/', (req, res) => {
  res.send(`
    <h2>XSS Bot</h2>
    <form method="POST" action="/report">
      <input type="text" name="url" value="http://localhost/?data=..." style="width: 500px;" />
      <button type="submit">Submit</button>
    </form>
  `);
});

app.listen(PORT, () => {
  console.log(`XSS bot running at port ${PORT}`);
});

