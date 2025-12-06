import { getDailyPuzzle } from './src/lib/daily'; (async () => { const puzzle = await getDailyPuzzle({ difficulty: 'expert', size: 6 }); console.log('result', puzzle?.id, puzzle?.size); })();
