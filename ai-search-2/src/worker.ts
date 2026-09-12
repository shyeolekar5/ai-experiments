/// <reference types="@cloudflare/workers-types" />
// Entry point for `wrangler deploy`. Routes /api/search; everything else
// falls through to the static frontend served via the ASSETS binding.

import { handleSearch, type Env } from "./server/search";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/search") {
      return handleSearch(request, env);
    }

    return env.ASSETS.fetch(request);
  },
};
