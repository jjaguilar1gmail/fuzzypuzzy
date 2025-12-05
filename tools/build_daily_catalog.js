const fs = require('fs');
const path = require('path');

const packsDir = path.resolve(__dirname, '..', 'frontend', 'public', 'packs');
const outputFile = path.resolve(__dirname, '..', 'frontend', 'public', 'daily_catalog.json');

/** @type {Array<{pack_id?: string, pack_slug: string, puzzle_id: string, difficulty: string, size: number, intermediate_level: number}>} */
const entries = [];

function walk(dir) {
  const dirents = fs.readdirSync(dir, { withFileTypes: true });
  for (const dirent of dirents) {
    const fullPath = path.join(dir, dirent.name);
    if (dirent.isDirectory()) {
      walk(fullPath);
    } else if (
      dirent.isFile() &&
      dirent.name.endsWith('.json') &&
      fullPath.includes(`${path.sep}puzzles${path.sep}`)
    ) {
      processPuzzle(fullPath);
    }
  }
}

function processPuzzle(puzzlePath) {
  try {
    const raw = fs.readFileSync(puzzlePath, 'utf8');
    const data = JSON.parse(raw);
    if (!data || !data.difficulty || !data.id || !data.size || !data.intermediate_level) {
      return;
    }
    const relFromPacks = path.relative(packsDir, puzzlePath);
    const segments = relFromPacks.split(path.sep);
    const puzzlesIndex = segments.indexOf('puzzles');
    if (puzzlesIndex <= 0) {
      return;
    }
    const slugParts = segments.slice(0, puzzlesIndex);
    const packSlug = slugParts.join('/');
    entries.push({
      pack_id: data.pack_id || slugParts[slugParts.length - 1],
      pack_slug: packSlug,
      puzzle_id: data.id,
      difficulty: data.difficulty,
      size: data.size,
      intermediate_level: data.intermediate_level,
    });
  } catch (err) {
    console.warn(`Skipping ${puzzlePath}: ${err.message}`);
  }
}

walk(packsDir);

const sortedEntries = entries.sort((a, b) => {
  if (a.pack_slug === b.pack_slug) {
    return a.puzzle_id.localeCompare(b.puzzle_id);
  }
  return a.pack_slug.localeCompare(b.pack_slug);
});

const output = {
  schema_version: '1.1',
  generated_at: new Date().toISOString(),
  entries: sortedEntries,
};

fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));
console.log(`Catalog written to ${outputFile} with ${entries.length} entries.`);
