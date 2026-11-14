import { NextRequest, NextResponse } from "next/server";
import { internalApiConfig, ownerFromGateway } from "@/lib/internal-api-config";

export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ path: string[] }> };

const permittedMethods = new Set(["GET", "POST"]);
const safePathSegment = /^[A-Za-z0-9._-]+$/;

async function proxy(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  if (!permittedMethods.has(request.method)) {
    return NextResponse.json({ detail: "Method not allowed" }, { status: 405, headers: { Allow: "GET, POST, OPTIONS" } });
  }

  const config = internalApiConfig(process.env);
  if (!config) {
    return NextResponse.json(
      { detail: "ForestProof API proxy is not configured for this deployment." },
      { status: 503 },
    );
  }

  let ownerSubject: string | null = null;
  if (config.owner) {
    ownerSubject = ownerFromGateway(request.headers, config.owner);
    if (!ownerSubject) {
      return NextResponse.json({ detail: "Owner authentication required" }, { status: 401 });
    }
    if (request.method === "POST" && request.headers.get("origin") !== config.owner.origin) {
      return NextResponse.json({ detail: "Forbidden" }, { status: 403 });
    }
  }

  const { path: segments } = await context.params;
  if (!segments.length || segments.some((segment) => segment === "." || segment === ".." || !safePathSegment.test(segment))) {
    return NextResponse.json({ detail: "Invalid API path" }, { status: 400 });
  }

  const incomingUrl = new URL(request.url);
  const target = `${config.base}/${segments.map(encodeURIComponent).join("/")}${incomingUrl.search}`;
  const headers = new Headers({ Accept: request.headers.get("accept") ?? "application/json" });
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);
  if (config.owner && ownerSubject) {
    headers.set("X-Forestproof-Internal-Token", config.owner.apiToken);
    headers.set("X-Forestproof-Owner-Subject", ownerSubject);
    headers.set("X-Forestproof-Require-Owner-Demo", "1");
  }

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "POST" ? await request.arrayBuffer() : undefined,
      cache: "no-store",
      // A redirect must never forward an internal service token to another host.
      redirect: "error",
    });
    const responseHeaders = new Headers();
    if (config.owner) responseHeaders.set("Cache-Control", "no-store");
    const responseContentType = upstream.headers.get("content-type");
    if (responseContentType) responseHeaders.set("Content-Type", responseContentType);
    const disposition = upstream.headers.get("content-disposition");
    if (disposition) responseHeaders.set("Content-Disposition", disposition);
    return new NextResponse(upstream.body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return NextResponse.json(
      { detail: "ForestProof API is temporarily unavailable." },
      { status: 502 },
    );
  }
}

export async function GET(request: NextRequest, context: RouteContext) {
  return proxy(request, context);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxy(request, context);
}

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: { Allow: "GET, POST, OPTIONS" } });
}
