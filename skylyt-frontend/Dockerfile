# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
RUN npm install -g bun
COPY package.json ./
RUN bun install
COPY . .
RUN bun run build

# Stage 2: Serve
FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]
