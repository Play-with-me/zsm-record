const fs = require('fs');
const { JSDOM } = require('jsdom');

process.on('unhandledRejection', (reason, promise) => {
  console.log('Unhandled Rejection:', reason);
  if (reason && reason.stack) console.log('Stack:', reason.stack);
});

const html = fs.readFileSync('index.html', 'utf-8');
const dom = new JSDOM(html, { runScripts: "dangerously", url: "http://localhost/#/" });

dom.window.Chart = class { constructor() {} };
dom.window.console.error = (msg) => console.log('ERROR:', msg);
dom.window.console.log = (...args) => console.log('LOG:', ...args);
dom.window.matchMedia = () => ({ matches: false });
dom.window.fetch = async (url) => {
  return { ok: true, status: 200, json: async () => ({}) };
};

try {
  const js = fs.readFileSync('temp.js', 'utf-8');
  dom.window.eval(js);
  
  dom.window.eval('if(typeof router !== "undefined") router().catch(e => console.log("router error", e, e.stack)); else console.log("router not defined")');
} catch (e) {
  console.log('Runtime Error:', e.message);
}
