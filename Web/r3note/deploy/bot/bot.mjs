import express from "express";
import puppeteer from "puppeteer";
import { readFileSync } from 'fs';

const app = express();
const HOST = '127.0.0.1'
const PORT = 3001;
const FLAG = readFileSync("/flag", "utf8");

const tokenQueue = [];
let isProcessing = false;
let browser = null;

const sleep = (d) => new Promise((r) => setTimeout(r, d));

const processTokenQueue = async () => {
  if (isProcessing || tokenQueue.length === 0) {
    return;
  }

  isProcessing = true;
  console.log(`Starting queue processing. Queue length: ${tokenQueue.length}`);
  
  while (tokenQueue.length > 0) {
    const token = tokenQueue.shift();
    try {
      console.log(`Processing token: ${token} (${tokenQueue.length} remaining in queue)`);
      await checkReport(token).catch(err => {
        console.error(`Error processing token ${token}:`, err);
      });
      console.log(`Completed processing token: ${token}`);
    } catch (error) {
      console.error(`Error processing token ${token}:`, error);
    }
  }
  
  isProcessing = false;
  console.log('Queue processing completed');
}

const addTokenToQueue = (token) => {
  tokenQueue.push(token);
  console.log(`Token added to queue. Queue length: ${tokenQueue.length}`);
  
  if (!isProcessing) {
    processTokenQueue();
  }
}

const checkReport = async (token) => {
  try {
    if (browser) {
      await browser.close();
      await sleep(2000);
      return;
    }

    browser = await puppeteer.launch({
      browser: "chrome",
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--user-data-dir=/tmp/chrome-userdata",
        "--breakpad-dump-location=/tmp/chrome-crashes"
      ]
    });

    const ctx = await browser.createBrowserContext();
    const page = await ctx.newPage();

    await page.goto("http://127.0.0.1:8080/", { timeout: 5000 });
    await page.evaluate((flag) => {
      localStorage.setItem("flag", flag);
    }, FLAG);

    console.log(`Checking report for token: ${token}`);

    await page.goto(`http://127.0.0.1:8080/share/${token}`, { timeout: 5000 });
    await sleep(5000);

    console.log(`Finished checking report for token: ${token}`);

  } catch (err) {
    console.log(err);
  } finally {
    if (browser) {
      await browser.close();
      await sleep(2000);
      browser = null;
    }
  }
}

app.use(express.json());

app.post("/api/share/report", (req, res) => {
  const token = req.body.token;
  if (token && typeof token === "string") {
    addTokenToQueue(token);
    res.status(200).json({
      status: "success",
      message: "Report submitted successfully. Thank you for your feedback!"
    });
  } else {
    res.status(400).send("Invalid token");
  }
});

app.listen(PORT, HOST, () => {
  console.log(`Listening on port ${PORT}`);
});
