// make.fun bounty news-image-20261125: one image summing up the world's news
// of Wednesday 25 November 2026.
//
// The poster (entry.png, beside this file) is drawn at build time by
// tools/draw_poster.py. This program checks that file against the contest
// limits and writes the same bytes to the output directory. Node standard
// library only, no network, no clock, no randomness: every run is identical.

import { chmodSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, "entry.png");
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const TARGET = join(OUT_DIR, "entry.png");

const MAX_BYTES = 1048576;
const MAX_SIDE = 1024;
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(message: string): never {
  console.error("news-image-20261125: " + message);
  process.exit(1);
}

// CRC-32 as PNG uses it (polynomial 0xEDB88320), table built once.
const CRC_TABLE = new Uint32Array(256);
for (let n = 0; n < 256; n++) {
  let c = n;
  for (let k = 0; k < 8; k++) {
    c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  }
  CRC_TABLE[n] = c >>> 0;
}

function crc32(bytes: Uint8Array, start: number, end: number): number {
  let c = 0xffffffff;
  for (let i = start; i < end; i++) {
    c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

// Walks every chunk of the PNG: signature, IHDR first, checksums, IEND last.
function inspectPng(png: Buffer): { width: number; height: number; chunks: number } {
  if (png.length > MAX_BYTES) fail(`image is ${png.length} bytes, over the ${MAX_BYTES} limit`);
  for (let i = 0; i < PNG_SIGNATURE.length; i++) {
    if (png[i] !== PNG_SIGNATURE[i]) fail("entry.png does not start with the PNG signature");
  }
  let offset = PNG_SIGNATURE.length;
  let width = 0;
  let height = 0;
  let chunks = 0;
  let sawData = false;
  let sawEnd = false;
  while (offset < png.length) {
    if (sawEnd) fail("bytes follow the IEND chunk");
    if (offset + 12 > png.length) fail("truncated chunk header");
    const length = png.readUInt32BE(offset);
    const type = png.toString("latin1", offset + 4, offset + 8);
    const dataEnd = offset + 8 + length;
    if (dataEnd + 4 > png.length) fail(`chunk ${type} runs past the end of the file`);
    if (crc32(png, offset + 4, dataEnd) !== png.readUInt32BE(dataEnd)) fail(`chunk ${type} has a bad checksum`);
    if (chunks === 0) {
      if (type !== "IHDR" || length !== 13) fail("first chunk is not a 13-byte IHDR");
      width = png.readUInt32BE(offset + 8);
      height = png.readUInt32BE(offset + 12);
    }
    if (type === "IDAT") sawData = true;
    if (type === "IEND") sawEnd = true;
    chunks++;
    offset = dataEnd + 4;
  }
  if (!sawData) fail("no IDAT chunk");
  if (!sawEnd) fail("no IEND chunk");
  if (width < 1 || height < 1) fail("image has a zero side");
  if (width > MAX_SIDE || height > MAX_SIDE) fail(`image is ${width}x${height}, over ${MAX_SIDE}x${MAX_SIDE}`);
  return { width, height, chunks };
}

const image = readFileSync(SOURCE);
const info = inspectPng(image);

// An empty MAKEFUN_OUTPUT_DIR would resolve to the working directory: refuse it.
if (OUT_DIR.trim() === "") fail("MAKEFUN_OUTPUT_DIR is set but empty");

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(TARGET, image);
// writeFileSync's mode is cut down by the umask, so set the readable mode outright.
chmodSync(TARGET, 0o644);

const written = readFileSync(TARGET);
if (!written.equals(image)) fail("the file written differs from the source image");

console.log(`wrote ${TARGET}: ${info.width}x${info.height} PNG, ${image.length} bytes, ${info.chunks} chunks`);
