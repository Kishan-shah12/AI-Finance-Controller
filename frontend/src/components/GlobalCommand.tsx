"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import { 
  GitMerge, 
  AlertTriangle, 
  Search, 
  BrainCircuit,
  MessageSquareText,
  Activity,
  History
} from "lucide-react";

export function GlobalCommand() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        
        <CommandGroup heading="Actions">
          <CommandItem onSelect={() => runCommand(() => router.push("/reconciliation"))}>
            <GitMerge className="mr-2 h-4 w-4" />
            <span>Run reconciliation</span>
          </CommandItem>
          <CommandItem onSelect={() => runCommand(() => router.push("/transactions"))}>
            <Search className="mr-2 h-4 w-4" />
            <span>Find transaction</span>
          </CommandItem>
        </CommandGroup>
        
        <CommandSeparator />
        
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => runCommand(() => router.push("/exceptions"))}>
            <AlertTriangle className="mr-2 h-4 w-4" />
            <span>Open exceptions</span>
          </CommandItem>
          <CommandItem onSelect={() => runCommand(() => router.push("/intelligence/settlement"))}>
            <BrainCircuit className="mr-2 h-4 w-4" />
            <span>Settlement intelligence</span>
          </CommandItem>
          <CommandItem onSelect={() => runCommand(() => router.push("/metrics"))}>
            <Activity className="mr-2 h-4 w-4" />
            <span>Metrics</span>
          </CommandItem>
          <CommandItem onSelect={() => runCommand(() => router.push("/agent"))}>
            <MessageSquareText className="mr-2 h-4 w-4" />
            <span>Ask ReconAI</span>
          </CommandItem>
          <CommandItem onSelect={() => runCommand(() => router.push("/audit"))}>
            <History className="mr-2 h-4 w-4" />
            <span>Audit trail</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}
