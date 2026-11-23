// news-image-20261123 entry program (Node 22, standard library only).
//
// The image is the entry: news/entry.png, drawn by news/build_image.py in the agent session
// that built this repository. This program puts exactly those bytes at /output/entry.png,
// where the sealed gate reads them, and refuses nothing: the gate weighs the file, and a
// non-zero exit would fail the run outright. It only says on stderr where the file is short of
// what the gate wants, so a broken build is visible in the dev run.
//
// Deterministic by construction: one read, one write, no clock, no randomness, no network.
//
// Outside the grader's container, point the two directories at local paths:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const SOURCE = join(BOT_DIR, 'news', 'entry.png');
const TARGET = join(OUTPUT_DIR, 'entry.png');

const MAX_BYTES = 1024 * 1024;

function warn(): void {
  try {
    const { size } = statSync(SOURCE);
    if (size > MAX_BYTES) console.error(`warning: entry.png is ${size} bytes, over the 1 MiB cap`);
  } catch {
    console.error(`warning: ${SOURCE} is missing`);
  }
}

mkdirSync(OUTPUT_DIR, { recursive: true });
copyFileSync(SOURCE, TARGET);
warn();
