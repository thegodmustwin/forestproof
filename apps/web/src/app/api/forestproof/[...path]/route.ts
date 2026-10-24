import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

type RouteContext = { params: { path: string[] } };

const permittedMethods = new Set(["GET", "POST"]);
const safePathSegment = /^[A-Za-z0-9._-]+$/;

function apiBase(): string | null {
  const configured = process.env.FORESTPROOF_API_INTERNAL_BASE_URL?.trim();
  if (!configured) return null;

  try {
    const url = new URL(configured);
    return (url.protocol === "http:" || url.protocol === "https:")
      ? configured.replace(/\/$/, "")
      : null;
  } catch {
    return null;
  }
}

async function proxy(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  if (!permittedMethods.has(request.method)) {
    return NextResponse.json({ detail: "Method not allowed" }, { status: 405, headers: { Allow: "GET, POST, OPTIONS" } });
  }

  const base = apiBase();
  if (!base) {
    return NextResponse.json(
      { detail: "ForestProof API proxy is not configured for this deployment." },
      { status: 503 },
    );
  }

  const segments = context.params.path;
  if (!segments.length || segments.some((segment) => !safePathSegment.test(segment))) {
    return NextResponse.json({ detail: "Invalid API path" }, { status: 400 });
  }

  const incomingUrl = new URL(request.url);
  const target = `${base}/${segments.map(encodeURIComponent).join("/")}${incomingUrl.search}`;
  const headers = new Headers({ Accept: request.headers.get("accept") ?? "application/json" });
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: request.method === "POST" ? await request.arrayBuffer() : undefined,
      cache: "no-store",
    });
    const responseHeaders = new Headers();
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
