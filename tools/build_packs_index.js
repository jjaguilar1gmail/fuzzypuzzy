const fs = require('fs');
const path = require('path');

const packsDir = path.resolve(__dirname, '..', 'frontend', 'public', 'packs');
const outputFile = path.join(packsDir, 'index.json');

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function listPackDirs() {
  if (!fs.existsSync(packsDir)) {
    throw new Error(`Packs directory not found at ${packsDir}`);
  }
  return fs
    .readdirSync(packsDir, { withFileTypes: true })
    .filter((dirent) => dirent.isDirectory())
    .filter((dirent) => dirent.name !== 'playground');
}

function collectPuzzleIds(puzzlesDir, metadata) {
  if (Array.isArray(metadata.puzzles) && metadata.puzzles.length > 0) {
    return metadata.puzzles;
  }
  if (!fs.existsSync(puzzlesDir)) {
    return [];
  }
  return fs
    .readdirSync(puzzlesDir)
    .filter((file) => file.endsWith('.json'))
    .map((file) => path.basename(file, '.json'))
    .sort((a, b) => a.localeCompare(b));
}

function buildPackEntry(packDirent) {
  const packPath = path.join(packsDir, packDirent.name);
  const metadataPath = path.join(packPath, 'metadata.json');
  if (!fs.existsSync(metadataPath)) {
    console.warn(`Skipping ${packDirent.name}: no metadata.json found.`);
    return null;
  }

  const metadata = readJson(metadataPath);
  const puzzlesDir = path.join(packPath, 'puzzles');
  const puzzleIds = collectPuzzleIds(puzzlesDir, metadata);
  const sizeCatalog = {};
  const computedDifficultyCounts = {};
  const hasDifficultyCounts =
    metadata.difficulty_counts && Object.keys(metadata.difficulty_counts).length > 0;

  for (const puzzleId of puzzleIds) {
    const puzzlePath = path.join(puzzlesDir, `${puzzleId}.json`);
    if (!fs.existsSync(puzzlePath)) {
      console.warn(`  ⚠️ Missing puzzle file ${puzzlePath}, skipping.`);
      continue;
    }
    let puzzleData;
    try {
      puzzleData = readJson(puzzlePath);
    } catch (error) {
      console.warn(`  ⚠️ Failed to parse ${puzzlePath}: ${error.message}`);
      continue;
    }
    const sizeKey = puzzleData.size ? String(puzzleData.size) : null;
    if (sizeKey) {
      sizeCatalog[sizeKey] = sizeCatalog[sizeKey] || [];
      sizeCatalog[sizeKey].push(puzzleData.id || puzzleId);
    }
    if (!hasDifficultyCounts && puzzleData.difficulty) {
      computedDifficultyCounts[puzzleData.difficulty] =
        (computedDifficultyCounts[puzzleData.difficulty] || 0) + 1;
    }
  }

  Object.values(sizeCatalog).forEach((list) => list.sort((a, b) => a.localeCompare(b)));

  const entry = {
    id: metadata.id || packDirent.name,
    title: metadata.title || metadata.id || packDirent.name,
    puzzle_count: puzzleIds.length,
    difficulty_counts: hasDifficultyCounts ? metadata.difficulty_counts : computedDifficultyCounts,
    size_catalog: sizeCatalog,
    created_at: metadata.created_at,
    updated_at: metadata.updated_at,
    description: metadata.description,
  };

  // Remove empty optional fields
  Object.entries(entry).forEach(([key, value]) => {
    const isEmptyObject =
      value && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length === 0;
    if (
      value === undefined ||
      value === null ||
      (typeof value === 'string' && value.trim() === '') ||
      isEmptyObject
    ) {
      delete entry[key];
    }
  });

  return entry;
}

function main() {
  const packEntries = [];
  const packDirs = listPackDirs();
  if (packDirs.length === 0) {
    console.warn('No pack directories found, writing empty index.');
  }
  for (const dirent of packDirs) {
    const entry = buildPackEntry(dirent);
    if (entry) {
      packEntries.push(entry);
    }
  }
  const sorted = packEntries.sort((a, b) => a.id.localeCompare(b.id));
  fs.writeFileSync(outputFile, JSON.stringify(sorted, null, 2));
  console.log(`Pack index written to ${outputFile} with ${sorted.length} entries.`);
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error('Failed to build pack index:', error);
    process.exit(1);
  }
}
