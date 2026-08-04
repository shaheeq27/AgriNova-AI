import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AgriNova AI — Precision Agriculture Platform",
  description:
    "AI-powered precision agriculture platform guiding farmers through the entire crop lifecycle — from seed to harvest.",
  keywords: "agriculture, AI, crop recommendation, farming, precision agriculture",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
