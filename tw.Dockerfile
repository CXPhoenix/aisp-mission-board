FROM node:22-alpine

WORKDIR /tw
COPY tailwind_styles/ /tw

RUN corepack enable pnpm
RUN pnpm install --force
