import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";
import { GlobalCommand } from "@/components/GlobalCommand";

const inter = Inter({ subsets: ["latin"] });

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
      <body className={`${inter.className} h-screen overflow-hidden flex bg-background text-foreground antialiased`}>
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Topbar />
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
        <GlobalCommand />
      </body>
    </html>
  );
}
