import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Skyline — Weather Intelligence Platform",
  description:
    "A calm, data-forward weather intelligence dashboard: live conditions, 5-day forecasts, an AI weather assistant, and a searchable history — built by K1 (Unq Innovators) for the PM Accelerator AI Engineer Intern technical assessment.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased font-body bg-canvas text-ink">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

