"use client";

import { Command, User, Menu } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useNav } from "@/components/layout/NavContext";

export function Topbar() {
  const { openMobileMenu } = useNav();

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b bg-background px-4 sm:px-6">
      <div className="flex items-center gap-3">
        {/* Mobile menu hamburger toggle button */}
        <button
          onClick={openMobileMenu}
          className="p-2 -ml-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors md:hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Mobile brand title */}
        <div className="flex flex-col md:hidden">
          <span className="font-bold tracking-tight text-foreground text-sm">RECON<span className="text-ai">AI</span></span>
          <span className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground">Controller</span>
        </div>

        {/* Desktop breadcrumb or page context placeholder */}
        <div className="hidden md:flex flex-col">
          {/* Page context space preserved for desktop */}
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <Badge variant="outline" className="bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 border-amber-500/20 px-2 sm:px-2.5 py-0.5 rounded-full font-medium text-[11px] sm:text-xs shrink-0">
          DEMO MODE
        </Badge>

        <div className="hidden lg:flex flex-col items-end mr-2">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className="font-medium text-amber-600/80">Demo data · Aug 26, 2026</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className="font-medium">
              Today · {new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date())}
            </span>
          </div>
        </div>

        <button 
          onClick={() => {
            // Trigger Cmd+K global command
            const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true });
            document.dispatchEvent(event);
          }}
          className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground border rounded-md px-3 py-1.5 bg-muted/30 hover:bg-muted/50 transition-colors"
          aria-label="Search or command palette"
        >
          <Command className="h-3.5 w-3.5" />
          <span className="text-xs font-medium">Cmd K</span>
        </button>

        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border text-primary shrink-0">
          <User className="h-4 w-4" />
        </div>
      </div>
    </header>
  );
}
