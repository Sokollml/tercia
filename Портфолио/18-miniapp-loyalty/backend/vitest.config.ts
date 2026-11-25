import { existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { defineConfig } from 'vitest/config';

/**
 * The source uses NodeNext ESM imports with explicit ".js" extensions (required
 * for the compiled Node output). This tiny resolver lets Vitest load the ".ts"
 * source behind those ".js" specifiers, so tests exercise the real modules.
 */
export default defineConfig({
  plugins: [
    {
      name: 'resolve-js-to-ts',
      enforce: 'pre',
      resolveId(source, importer) {
        if (
          importer &&
          source.endsWith('.js') &&
          (source.startsWith('./') || source.startsWith('../'))
        ) {
          const candidate = resolve(dirname(importer), source.replace(/\.js$/, '.ts'));
          if (existsSync(candidate)) return candidate;
        }
        return null;
      },
    },
  ],
  test: {
    include: ['test/**/*.test.ts'],
    // Ignore macOS AppleDouble metadata files ("._*") that some filesystems
    // create alongside every file — they are not real test modules.
    exclude: ['**/node_modules/**', '**/dist/**', '**/._*'],
    environment: 'node',
  },
});
