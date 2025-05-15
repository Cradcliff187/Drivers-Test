import fs from 'fs/promises';
import path from 'path';

export async function handler(event) {
  const params = new URLSearchParams(event.queryStringParameters);
  const n = Math.min(Number(params.get('count') || 20), 50);

  try {
    if (!global.bank) {
      const filePath = path.join(process.cwd(), 'public', 'test_bank.json');
      const raw = await fs.readFile(filePath, 'utf8');
      global.bank = JSON.parse(raw);
    }

    const sample = [...global.bank]
      .sort(() => 0.5 - Math.random())
      .slice(0, n)
      .map(({ explanation, ...q }) => q);

    return {
      statusCode: 200,
      headers: {
        'content-type': 'application/json'
      },
      body: JSON.stringify(sample)
    };
  } catch (err) {
    return { statusCode: 500, body: String(err) };
  }
} 