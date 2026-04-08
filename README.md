# WaveAPI Documentation

WaveAPI is a unified AI model API gateway that provides a single endpoint to access all leading AI models including GPT, Claude, Gemini, Sora, VEO, Kling, and more.

- **Documentation**: [docs.qingbo.dev](https://docs.qingbo.dev)
- **API Platform**: [qingbo.dev](https://qingbo.dev)
- **Dashboard**: [qingbo.dev/dashboard/keys](https://qingbo.dev/dashboard/keys)

## Features

- **OpenAI Compatible** — Drop-in replacement for OpenAI SDK, just change the `base_url`
- **Multi-Model Access** — One API key for text, image, video, and audio generation models
- **Unified Task System** — Async task management for image and video generation via `/v1/tasks`
- **Multi-Language Docs** — Available in English, Simplified Chinese, Traditional Chinese, and Japanese

## Documentation Structure

```
cn/          # Simplified Chinese (primary)
en/          # English
jp/          # Japanese
zh-Hant/     # Traditional Chinese
```

Each language contains:
- **Docs** — Getting started, authentication, core concepts (sync/async, task system, streaming)
- **API Reference** — Text generation, image generation, video generation, audio, tools, task management

## Development

```bash
pnpm install
npx mint dev
```

Preview at `http://localhost:3000`.

## Tech Stack

Built with [Mintlify](https://mintlify.com) using the `maple` theme.

## License

Proprietary. All rights reserved.
