import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { BottomNav } from "@/components/layout/BottomNav";
import { NavProvider } from "@/components/layout/NavContext";
import { GlobalCommand } from "@/components/GlobalCommand";

const inter = Inter({ subsets: ["latin"] });

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  title: "ReconAI - AI Finance Controller",
  description: "AI-powered financial reconciliation platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} h-[100dvh] overflow-hidden flex bg-background text-foreground antialiased`}>
        <NavProvider>
          <Sidebar />
          <div className="flex flex-col flex-1 overflow-hidden min-w-0">
            <Topbar />
            <main className="flex-1 overflow-y-auto pb-16 md:pb-0 min-w-0">
              {children}
            </main>
            <BottomNav />
          </div>
          <GlobalCommand />
        </NavProvider>
      </body>
    </html>
  );
}
