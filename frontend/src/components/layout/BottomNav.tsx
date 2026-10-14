"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  LayoutDashboard, 
  GitMerge, 
  AlertTriangle, 
  BrainCircuit, 
  MessageSquareText 
} from "lucide-react";

export function BottomNav() {
  const pathname = usePathname();

  const tabs = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Recon", href: "/reconciliation", icon: GitMerge },
    { name: "Exceptions", href: "/exceptions", icon: AlertTriangle },
    { name: "Intel", href: "/intelligence/settlement", icon: BrainCircuit },
    { name: "AI Agent", href: "/agent", icon: MessageSquareText },
  ];

  return (
    <nav 
      aria-label="Mobile Bottom Navigation" 
      className="fixed bottom-0 left-0 right-0 z-40 bg-background/95 backdrop-blur border-t flex items-center justify-around py-1.5 px-1 md:hidden shadow-lg safe-bottom"
    >
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = tab.href === "/" 
          ? pathname === "/" 
          : pathname === tab.href || pathname?.startsWith(tab.href + "/");

        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={cn(
              "flex flex-col items-center justify-center flex-1 py-1 px-1 rounded-md text-[10px] font-medium transition-colors",
              isActive 
                ? "text-primary font-semibold" 
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <div className={cn(
              "p-1 rounded-full transition-all",
              isActive && "bg-primary/10 text-primary"
            )}>
              <Icon className="h-4 w-4" />
            </div>
            <span className="mt-0.5 truncate max-w-[64px]">{tab.name}</span>
          </Link>
        );
      })}
    </nav>
  );
}
