"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  LayoutDashboard, 
  GitMerge, 
  AlertTriangle, 
  Search, 
  BrainCircuit,
  MessageSquareText,
  Activity,
  Settings,
  History,
  PlaySquare
} from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Overview", group: true },
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    
    { name: "Reconciliation", group: true },
    { name: "Judge Demo", href: "/demo", icon: PlaySquare },
    { name: "Command Center", href: "/reconciliation", icon: GitMerge },
    { name: "Transactions", href: "/transactions", icon: Search },
    { name: "Exceptions", href: "/exceptions", icon: AlertTriangle },
    
    { name: "Finance Intelligence", group: true },
    { name: "Settlement Intel", href: "/intelligence/settlement", icon: BrainCircuit },
    { name: "AI Controller", href: "/agent", icon: MessageSquareText },
    
    { name: "Control", group: true },
    { name: "Audit Trail", href: "/audit", icon: History },
    { name: "System Metrics", href: "/metrics", icon: Activity },
    
    { name: "System", group: true },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <div className="flex h-full w-64 flex-col border-r bg-background text-sm">
      <div className="flex h-16 shrink-0 items-center border-b px-6">
        <div className="flex flex-col">
          <span className="font-bold tracking-tight text-foreground">RECON<span className="text-ai">AI</span></span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">AI Finance Controller</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto py-6">
        <nav className="space-y-1 px-4">
          {navItems.map((item, index) => {
            if (item.group) {
              return (
                <div key={index} className="pt-4 pb-2 px-2 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                  {item.name}
                </div>
              );
            }
            
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
            
            return (
              <Link
                key={item.href}
                href={item.href!}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-primary text-primary-foreground" 
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
              >
                {Icon && <Icon className="h-4 w-4" />}
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="shrink-0 border-t p-4 space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Environment</span>
          <span className="flex items-center gap-1.5 font-medium text-amber-600">
            <span className="h-2 w-2 rounded-full bg-amber-500"></span>
            Demo Data
          </span>
        </div>
        <div className="flex items-center justify-between text-xs">
          <span className="text-muted-foreground">Backend API</span>
          <span className="flex items-center gap-1.5 font-medium text-success">
            <span className="h-2 w-2 rounded-full bg-success"></span>
            Online
          </span>
        </div>
      </div>
    </div>
  );
}
