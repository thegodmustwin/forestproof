/** Server-side configuration for the Next.js API proxy.
 * The owner demo is an isolated synthetic development mode, not user auth.
 */
export type InternalApiConfig = { base: string; ownerDemoToken?: string };

const invalidTokenCharacter = /[^A-Za-z0-9_-]/;

export function internalApiConfig(env: NodeJS.ProcessEnv): InternalApiConfig | null {
  const configured = env.FORESTPROOF_API_INTERNAL_BASE_URL?.trim();
  const mode = env.FORESTPROOF_API_MODE ?? "demo";
  if (!configured || (mode !== "demo" && mode !== "owner_demo")) return null;
  try {
    const url = new URL(configured);
    if ((url.protocol !== "http:" && url.protocol !== "https:") || url.username || url.password || url.search || url.hash) return null;
    if (mode === "owner_demo") {
      const token = env.FORESTPROOF_INTERNAL_API_TOKEN;
      // Until an authenticated service network exists, never forward the
      // internal token to DNS names or non-loopback hosts.
      if (!token || token.length < 43 || token.length > 128 || invalidTokenCharacter.test(token)
          || !["127.0.0.1", "[::1]"].includes(url.hostname)) return null;
      return { base: configured.replace(/\/$/, ""), ownerDemoToken: token };
    }
    return { base: configured.replace(/\/$/, "") };
  } catch {
    return null;
  }
}
