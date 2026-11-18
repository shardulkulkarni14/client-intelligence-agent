import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";
import ApiStatus from "@/components/ApiStatus";
import "./globals.css";

export const metadata: Metadata = {
  title: "Client briefings",
  description: "A thin view over the client-intel API",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <span className="title">Client briefings</span>
          <nav>
            <Link href="/">Briefing</Link>
            <Link href="/portfolio">Portfolio</Link>
          </nav>
          <ApiStatus />
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
