/// <reference types="@cloudflare/workers-types" />
// Entry point for `wrangler deploy`. Routes /api/* to handlers; everything
// else falls through to the static assets built by `astro build` (./dist),
// served via the ASSETS binding configured in wrangler.jsonc.

import { handleEnquire, type Env } from "./server/enquire";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/enquire") {
      return handleEnquire(request, env);
    }

    return env.ASSETS.fetch(request);
  },
};
