import fs from 'fs/promises';

export default async (req) => {
  const url = new URL(req.url);
  const count = Math.min(Number(url.searchParams.get('count') || 20), 50);

  if (!global.bank) {
    const raw = await fs.readFile('public/test_bank.json', 'utf8');
    global.bank = JSON.parse(raw);
  }

  const sample = global.bank
    .sort(() => 0.5 - Math.random())
    .slice(0, count)
    .map(({ explanation, ...q }) => q);

  return new Response(JSON.stringify(sample), {
    headers: {
      'content-type': 'application/json'
    }
  });
}; 