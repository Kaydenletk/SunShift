import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import path from 'node:path';

const constantsPath = path.join(
  process.cwd(),
  'src/components/landing/constants.ts'
);
const source = readFileSync(constantsPath, 'utf8');

test('landing navigation uses root-qualified hash links', () => {
  assert.match(source, /label: 'Features', href: '\/#features'/);
  assert.match(source, /label: 'Architecture', href: '\/#architecture'/);
  assert.match(source, /label: 'Pricing', href: '\/#pricing'/);
  assert.match(source, /label: 'Docs', href: '\/#docs'/);
});

test('feature entries declare destination hrefs', () => {
  assert.match(source, /export const features[\s\S]*?href: /);
});

test('story moments and ADR links declare destination hrefs', () => {
  assert.match(source, /export const storyMoments[\s\S]*?href: /);
  assert.match(source, /export const adrLinks[\s\S]*?href: /);
});

test('repo URL uses the correct casing', () => {
  assert.match(source, /REPO_URL = 'https:\/\/github\.com\/Kaydenletk\/SunShift'/);
});
