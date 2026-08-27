"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Shield, Lock } from "lucide-react";

export default function SettingsPage() {
  const [thresholds, setThresholds] = useState({
    auto: 80,
    review: 40
  });

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure system parameters and automation policies.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div className="md:col-span-1 space-y-4">
          <nav className="flex flex-col space-y-1">
            <a href="#" className="px-3 py-2 text-sm font-medium bg-muted rounded-md text-foreground">Automation Policy</a>
            <a href="#" className="px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted/50 rounded-md">Providers</a>
            <a href="#" className="px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted/50 rounded-md">System Status</a>
            <a href="#" className="px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted/50 rounded-md">Demo Mode</a>
          </nav>
        </div>

        <div className="md:col-span-2 space-y-8">
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" /> Automation Policy
              </CardTitle>
              <CardDescription>
                ReconAI optimizes for safe automation — not maximum automation.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-8">
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-base font-semibold">Safe Automation Visualization</Label>
                  <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-200">
                    <Lock className="h-3 w-3 mr-1" /> Locked Test Config
                  </Badge>
                </div>
                
                {/* Safe Automation Component */}
                <div className="pt-6 pb-2">
                  <div className="relative h-2 w-full bg-muted rounded-full overflow-hidden">
                    {/* Auto */}
                    <div className="absolute top-0 bottom-0 right-0 bg-success/20" style={{ left: `${thresholds.auto}%` }}></div>
                    {/* Review */}
                    <div className="absolute top-0 bottom-0 bg-amber-500/20" style={{ left: `${thresholds.review}%`, right: `${100 - thresholds.auto}%` }}></div>
                    {/* Exception */}
                    <div className="absolute top-0 bottom-0 left-0 bg-destructive/20" style={{ right: `${100 - thresholds.review}%` }}></div>
                    
                    {/* Threshold markers */}
                    <div className="absolute top-[-4px] bottom-[-4px] w-1 bg-background border-2 border-amber-500 rounded-full z-10" style={{ left: `calc(${thresholds.review}% - 2px)` }}></div>
                    <div className="absolute top-[-4px] bottom-[-4px] w-1 bg-background border-2 border-success rounded-full z-10" style={{ left: `calc(${thresholds.auto}% - 2px)` }}></div>
                  </div>
                  
                  <div className="relative mt-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground h-6">
                    <div className="absolute left-0 text-destructive text-left w-20">Exception</div>
                    <div className="absolute text-amber-600 text-center w-20 -translate-x-1/2" style={{ left: `${(thresholds.review + thresholds.auto) / 2}%` }}>Review</div>
                    <div className="absolute right-0 text-success text-right w-20">Auto-Match</div>
                  </div>
                  
                  <div className="relative mt-2 text-xs font-mono text-muted-foreground h-4">
                    <div className="absolute left-0">0%</div>
                    <div className="absolute -translate-x-1/2" style={{ left: `${thresholds.review}%` }}>{thresholds.review}%</div>
                    <div className="absolute -translate-x-1/2" style={{ left: `${thresholds.auto}%` }}>{thresholds.auto}%</div>
                    <div className="absolute right-0">100%</div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Review Threshold</Label>
                  <Input value={thresholds.review} readOnly disabled className="bg-muted/50" />
                  <p className="text-[10px] text-muted-foreground uppercase">Scores below this are exceptions</p>
                </div>
                <div className="space-y-2">
                  <Label>Auto-Match Threshold</Label>
                  <Input value={thresholds.auto} readOnly disabled className="bg-muted/50" />
                  <p className="text-[10px] text-muted-foreground uppercase">Scores above this are auto-resolved</p>
                </div>
              </div>

              <div className="p-4 bg-muted/20 border rounded-lg text-sm text-muted-foreground">
                <Lock className="h-4 w-4 inline-block mr-2 text-foreground" />
                These thresholds are currently locked to evaluate the frozen test set fairly. They cannot be modified in the normal UI.
              </div>
              
            </CardContent>
          </Card>
          
        </div>
      </div>
      
    </div>
  );
}
