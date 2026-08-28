"use client";

import { Bell, Command, User, ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function Topbar() {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b bg-background px-6">
      <div className="flex flex-col">
        {/* Placeholder for dynamic breadcrumbs or page context, to be injected by layout if needed, or we just leave empty since page content has its own headers */}
      </div>

      <div className="flex items-center gap-4">
        <Badge variant="outline" className="bg-amber-500/10 text-amber-600 hover:bg-amber-500/20 border-amber-500/20 px-2.5 py-0.5 rounded-full font-medium">
          DEMO MODE
        </Badge>

        <div className="flex flex-col items-end mr-2">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className="font-medium text-amber-600/80">Demo data · Aug 26, 2026</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className="font-medium">
              Today · {new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date())}
            </span>
          </div>
        </div>

        <button className="flex items-center gap-2 text-sm text-muted-foreground border rounded-md px-3 py-1.5 bg-muted/30 hover:bg-muted/50 transition-colors">
          <Command className="h-3.5 w-3.5" />
          <span className="text-xs font-medium">Cmd K</span>
        </button>

        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center border text-primary">
          <User className="h-4 w-4" />
        </div>
      </div>
    </header>
  );
}
