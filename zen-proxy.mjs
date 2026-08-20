#!/usr/bin/env node
// zen-proxy.mjs -- local proxy that lets Claude Code talk to OpenCode Zen.
//
// Claude Code speaks the Anthropic Messages API. OpenCode Zen exposes an
// Anthropic-compatible /v1/messages endpoint, so this proxy mostly passes
// requests straight through: it injects your Zen key, rewrites the model
// (stripping the "[1m]"-style context hints some launchers append), and
// relays the SSE stream back, adding keepalive pings so long responses
// don't time out.
//
// Config via environment:
//   ZEN_API_KEY    your OpenCode Zen key (required, sk-...)
//   ZEN_HOST       listen address (default 127.0.0.1)
//   ZEN_PORT       listen port (default 8787)
//   ZEN_UPSTREAM   upstream base URL (default https://opencode.ai/zen/v1/messages)
//   ZEN_MODEL      if set, force every request to use this model
//   ZEN_QUIET=1    suppress request logging
import http from 'node:http';

const HOST = process.env.ZEN_HOST || '127.0.0.1';
const PORT = Number(process.env.ZEN_PORT || 8787);
const UPSTREAM = (process.env.ZEN_UPSTREAM || 'https://opencode.ai/zen/v1/messages').replace(/\/+$/, '');
const KEY = process.env.ZEN_API_KEY || '';
const FORCE_MODEL = process.env.ZEN_MODEL || '';
const QUIET = process.env.ZEN_QUIET === '1';

if (!KEY) {
  console.error('zen-proxy: ZEN_API_KEY is required (run the installer or add it to ~/.zen-claude/.env)');
  process.exit(1);
}

function log(...args) {
  if (!QUIET) console.log(new Date().toISOString(), ...args);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

function rewriteModel(name) {
  if (FORCE_MODEL) return FORCE_MODEL;
  return String(name || '').replace(/\s*\[\d+[kKmM]+\]/g, '').trim();
}

function estimateTokens(payload) {
  try {
    return Math.ceil(JSON.stringify(payload).length / 4);
  } catch {
    return 1;
  }
}

async function proxy(req, res, target, overrideBody) {
  const headers = {
    authorization: `Bearer ${KEY}`,
    'x-api-key': KEY,
    'content-type': 'application/json',
    'anthropic-version': req.headers['anthropic-version'] || '2023-06-01',
  };
  for (const h of ['anthropic-beta', 'user-agent', 'accept', 'accept-language']) {
    if (req.headers[h]) headers[h] = req.headers[h];
  }

  let body = overrideBody;
  if (body === undefined && req.method !== 'GET' && req.method !== 'HEAD') {
    body = await readBody(req);
  }

  const controller = new AbortController();
  res.on('close', () => controller.abort());

  const upstream = await fetch(target, {
    method: req.method,
    headers,
    body,
    signal: controller.signal,
  });

  const outHeaders = {};
  for (const h of ['content-type', 'cache-control']) {
    const v = upstream.headers.get(h);
    if (v) outHeaders[h] = v;
  }
  const isSSE = (outHeaders['content-type'] || '').includes('text/event-stream');
  if (isSSE) {
    outHeaders['cache-control'] = 'no-cache';
    outHeaders['x-accel-buffering'] = 'no';
  }
  res.writeHead(upstream.status, outHeaders);

  if (upstream.body) {
    const reader = upstream.body.getReader();
    let last = Date.now();
    const timer = isSSE
      ? setInterval(() => {
          if (Date.now() - last >= 10000) {
            try { res.write(': ping\n\n'); } catch { /* client gone */ }
            last = Date.now();
          }
        }, 5000)
      : null;
    try {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        last = Date.now();
        try { res.write(value); } catch { break; }
      }
    } catch (err) {
      log('stream aborted:', err && err.message);
    } finally {
      if (timer) clearInterval(timer);
    }
  }
  try { res.end(); } catch { /* client already closed */ }
}

const server = http.createServer(async (req, res) => {
  req.on('error', () => {});
  res.on('error', () => {});
  try {
    const url = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);

    if (req.method === 'GET' && url.pathname === '/health') {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ ok: true }));
      return;
    }

    if (req.method === 'GET' && (url.pathname === '/v1/models' || url.pathname === '/models')) {
      await proxy(req, res, 'https://opencode.ai/zen/v1/models');
      return;
    }

    if (req.method === 'POST' && (url.pathname === '/v1/messages' || url.pathname === '/v1/messages/count_tokens' || url.pathname === '/v1/count_tokens')) {
      const raw = await readBody(req);

      if (url.pathname.endsWith('/count_tokens')) {
        let payload = {};
        try { payload = JSON.parse(raw); } catch { /* keep {} */ }
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify({ input_tokens: estimateTokens(payload), output_tokens: 0 }));
        return;
      }

      let body = raw;
      let model = '?';
      try {
        const parsed = JSON.parse(raw);
        if (parsed.model) {
          model = parsed.model;
          parsed.model = rewriteModel(parsed.model);
        }
        body = JSON.stringify(parsed);
      } catch { /* forward raw */ }
      log('messages ->', model, '=>', JSON.parse(body).model);
      await proxy(req, res, UPSTREAM + url.search, body);
      return;
    }

    res.writeHead(404, { 'content-type': 'application/json' });
    res.end(JSON.stringify({ error: { type: 'not_found', message: `${req.method} ${url.pathname}` } }));
  } catch (err) {
    log('error:', err && err.message);
    if (!res.headersSent) {
      res.writeHead(502, { 'content-type': 'application/json' });
    }
    try {
      res.end(JSON.stringify({
        type: 'error',
        error: { type: 'proxy_error', message: String((err && err.message) || err) },
      }));
    } catch { /* client gone */ }
  }
});

server.listen(PORT, HOST, () => {
  log(`zen-proxy listening on http://${HOST}:${PORT}`);
  log(`upstream ${UPSTREAM}`);
});
