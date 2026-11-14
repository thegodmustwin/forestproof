import { timingSafeEqual } from "node:crypto";

/** Server-side configuration for the synthetic owner gateway and API proxy. */
type OwnerAccess = { apiToken: string; gatewayToken: string; origin: string; subject: string };
export type InternalApiConfig = { base: string; owner?: OwnerAccess };

const invalidTokenCharacter = /[^A-Za-z0-9_-]/;
const invalidSubjectCharacter = /[^a-z0-9_-]/;

function validToken(value: string | undefined): value is string {
  return value !== undefined && value.length >= 43 && value.length <= 128 && !invalidTokenCharacter.test(value);
}

export function ownerFromGateway(headers: Headers, owner: OwnerAccess): string | null {
  const assertion = headers.get("x-forestproof-owner-gateway-token");
  if (!assertion || assertion.length !== owner.gatewayToken.length || invalidTokenCharacter.test(assertion)
      || !timingSafeEqual(Buffer.from(assertion), Buffer.from(owner.gatewayToken))) return null;
  const subject = headers.get("x-forestproof-owner-subject");
  return subject === owner.subject ? subject : null;
}

function loopbackOwnerOrigin(configured: string | undefined): string | null {
  if (!configured) return null;
  try {
    const url = new URL(configured);
    // The owner gateway listens only on IPv4 loopback through an SSH tunnel.
    // Require an explicit port and exact origin, with no path or credentials.
    if (url.protocol !== "http:" || url.hostname !== "127.0.0.1" || !url.port
        || configured !== url.origin) return null;
    return url.origin;
  } catch {
    return null;
  }
}

export function internalApiConfig(env: NodeJS.ProcessEnv): InternalApiConfig | null {
  const configured = env.FORESTPROOF_API_INTERNAL_BASE_URL?.trim();
  const mode = env.FORESTPROOF_API_MODE ?? "demo";
  if (!configured || (mode !== "demo" && mode !== "owner_demo")) return null;
  try {
    const url = new URL(configured);
    if ((url.protocol !== "http:" && url.protocol !== "https:") || url.username || url.password || url.search || url.hash) return null;
    if (mode === "owner_demo") {
      const apiToken = env.FORESTPROOF_INTERNAL_API_TOKEN;
      const gatewayToken = env.FORESTPROOF_OWNER_GATEWAY_TOKEN;
      const origin = loopbackOwnerOrigin(env.FORESTPROOF_OWNER_GATEWAY_ORIGIN);
      const subject = env.FORESTPROOF_OWNER_SUBJECT;
      // Until an authenticated service network exists, never forward the
      // internal token to DNS names or non-loopback hosts.
      if (!validToken(apiToken) || !validToken(gatewayToken) || gatewayToken === apiToken
          || !subject || subject.length > 63 || !/^[a-z]/.test(subject) || invalidSubjectCharacter.test(subject)
          || !origin || !["127.0.0.1", "[::1]"].includes(url.hostname)) return null;
      return { base: configured.replace(/\/$/, ""), owner: { apiToken, gatewayToken, origin, subject } };
    }
    return { base: configured.replace(/\/$/, "") };
  } catch {
    return null;
  }
}
