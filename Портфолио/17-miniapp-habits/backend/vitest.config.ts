import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Исключаем macOS AppleDouble-файлы (._*), которые появляются на внешних
    // дисках/сетевых шарах и ломают трансформацию как «битые» модули.
    exclude: ['**/node_modules/**', '**/dist/**', '**/._*'],
  },
});
