import type { Metadata } from "next";
import "./globals.css";
import "maplibre-gl/dist/maplibre-gl.css";
import { AppShell } from "@/components/app-shell";

export const metadata: Metadata = {
  title: "ForestProof | Evidence to action",
  description: "Environmental evidence, intervention and accountability control plane.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
