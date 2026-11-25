# ── Сборка ────────────────────────────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# ── Рантайм ───────────────────────────────────────────────────────────────
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json* ./
# Только прод-зависимости.
RUN npm install --omit=dev
COPY --from=build /app/dist ./dist
# Миграции нужны в рантайме — сервер применяет их при старте.
COPY --from=build /app/db ./db
EXPOSE 8080
CMD ["node", "dist/server.js"]
