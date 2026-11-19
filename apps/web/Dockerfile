FROM node:24-alpine AS dependencies

WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci

FROM node:24-alpine AS builder

WORKDIR /workspace/apps/web
ENV NODE_ENV=production
COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/web/ ./
COPY packages/ui/ /workspace/packages/ui/
RUN npm run build

FROM node:24-alpine AS runner

WORKDIR /workspace/apps/web
ENV NODE_ENV=production

COPY --from=builder /workspace/apps/web/package.json ./package.json
COPY --from=builder /workspace/apps/web/package-lock.json ./package-lock.json
COPY --from=builder /workspace/apps/web/next.config.mjs ./next.config.mjs
COPY --from=builder /workspace/apps/web/node_modules ./node_modules
COPY --from=builder /workspace/apps/web/.next ./.next

EXPOSE 3000
CMD ["sh", "-c", "exec npm run start -- -H 0.0.0.0 -p ${PORT:-3000}"]
