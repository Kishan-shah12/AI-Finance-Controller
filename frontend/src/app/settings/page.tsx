"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Shield, Lock, Activity, Server, Database, Globe, PlayCircle, Key } from "lucide-react";
import { api } from "@/lib/api";

type Tab = "automation" | "providers" | "system" | "demo";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("automation");
  const [dependencies, setDependencies] = useState<any>(null);
  const [razorpayStatus, setRazorpayStatus] = useState<any>(null);
  
  const [thresholds, setThresholds] = useState({
    auto: 80,
    review: 40
  });

  useEffect(() => {
    // Read initial hash
    if (typeof window !== 'undefined') {
      const hash = window.location.hash.replace('#', '') as Tab;
      if (["automation", "providers", "system", "demo"].includes(hash)) {
        setActiveTab(hash);
      }
    }

    const loadData = async () => {
      const [deps, rp] = await Promise.all([
        api.getDependenciesHealth(),
        api.getRazorpayStatus()
      ]);
      setDependencies(deps);
      setRazorpayStatus(rp);
    };
    loadData();
  }, []);

  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  const getStatusColor = (status: string) => {
    if (status === "HEALTHY" || status === "ok" || status === "configured") return "text-success bg-success/10 border-success/20";
    if (status === "NOT_CONFIGURED" || status === "not_configured") return "text-muted-foreground bg-muted border-muted-foreground/20";
    return "text-destructive bg-destructive/10 border-destructive/20";
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure system parameters and view system status.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <div className="md:col-span-1 space-y-4">
          <nav className="flex flex-col space-y-1" role="tablist" aria-label="Settings navigation">
            <button 
              role="tab"
              aria-selected={activeTab === 'automation'}
              onClick={() => handleTabChange("automation")}
              className={`px-3 py-2 text-sm font-medium text-left rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-primary ${activeTab === 'automation' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Automation Policy
            </button>
            <button 
              role="tab"
              aria-selected={activeTab === 'providers'}
              onClick={() => handleTabChange("providers")}
              className={`px-3 py-2 text-sm font-medium text-left rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-primary ${activeTab === 'providers' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Providers
            </button>
            <button 
              role="tab"
              aria-selected={activeTab === 'system'}
              onClick={() => handleTabChange("system")}
              className={`px-3 py-2 text-sm font-medium text-left rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-primary ${activeTab === 'system' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              System Status
            </button>
            <button 
              role="tab"
              aria-selected={activeTab === 'demo'}
              onClick={() => handleTabChange("demo")}
              className={`px-3 py-2 text-sm font-medium text-left rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-primary ${activeTab === 'demo' ? 'bg-muted text-foreground' : 'text-muted-foreground hover:bg-muted/50'}`}
            >
              Demo Mode
            </button>
          </nav>
        </div>

        <div className="md:col-span-2 space-y-8">
          
          {activeTab === "automation" && (
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
                      <div className="absolute top-0 bottom-0 right-0 bg-success/20" style={{ left: `${thresholds.auto}%` }}></div>
                      <div className="absolute top-0 bottom-0 bg-amber-500/20" style={{ left: `${thresholds.review}%`, right: `${100 - thresholds.auto}%` }}></div>
                      <div className="absolute top-0 bottom-0 left-0 bg-destructive/20" style={{ right: `${100 - thresholds.review}%` }}></div>
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
          )}

          {activeTab === "providers" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-primary" /> Connected Providers
                </CardTitle>
                <CardDescription>
                  Manage external payment gateways, core banking integrations, and intelligent models.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                <div className="flex items-center justify-between p-4 border rounded-lg bg-card">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <Key className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Razorpay (Test Mode)</p>
                      <p className="text-xs text-muted-foreground">Payment Gateway</p>
                    </div>
                  </div>
                  {razorpayStatus ? (
                    <Badge variant="outline" className={getStatusColor(razorpayStatus.status || (razorpayStatus.configured ? 'configured' : 'not_configured'))}>
                      {razorpayStatus.status || (razorpayStatus.configured ? 'CONFIGURED' : 'NOT CONFIGURED')}
                    </Badge>
                  ) : (
                    <span className="text-xs text-muted-foreground">Checking...</span>
                  )}
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg bg-card">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <Database className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Synthetic Data Provider</p>
                      <p className="text-xs text-muted-foreground">Demo Data Source</p>
                    </div>
                  </div>
                  <Badge variant="outline" className={getStatusColor(dependencies?.synthetic_provider || 'not_configured')}>
                    {dependencies?.synthetic_provider?.replace('_', ' ') || 'NOT CONFIGURED'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg bg-card">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center">
                      <Activity className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">LLM Provider (Google Gemini)</p>
                      <p className="text-xs text-muted-foreground">Intelligence Engine</p>
                    </div>
                  </div>
                  <Badge variant="outline" className={getStatusColor(dependencies?.llm_provider || 'not_configured')}>
                    {dependencies?.llm_provider?.replace('_', ' ') || 'NOT CONFIGURED'}
                  </Badge>
                </div>
                
              </CardContent>
            </Card>
          )}

          {activeTab === "system" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Server className="h-5 w-5 text-primary" /> System Status
                </CardTitle>
                <CardDescription>
                  Real-time health of core dependencies and backend services.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {dependencies ? (
                  <div className="space-y-4">
                    {Object.entries(dependencies).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center py-2 border-b last:border-0">
                        <span className="text-sm font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                        <Badge variant="outline" className={getStatusColor(value as string)}>
                          {String(value).replace(/_/g, ' ')}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center p-8 text-muted-foreground">
                    <Activity className="animate-pulse h-6 w-6 mr-2" />
                    Checking system health...
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === "demo" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PlayCircle className="h-5 w-5 text-primary" /> Demo Configuration
                </CardTitle>
                <CardDescription>
                  Settings for the deterministic Judge Demo mode.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Demo Provider</Label>
                    <Input value="SYNTHETIC" readOnly disabled className="bg-muted/50 font-mono text-sm" />
                  </div>
                  <div className="space-y-2">
                    <Label>Deterministic Seed</Label>
                    <Input value="42" readOnly disabled className="bg-muted/50 font-mono text-sm" />
                  </div>
                </div>

                <div className="p-4 bg-muted/20 border rounded-lg text-sm text-muted-foreground">
                  <Lock className="h-4 w-4 inline-block mr-2 text-foreground" />
                  The Demo configuration is strictly frozen to preserve repeatable evaluation outcomes.
                </div>
                
              </CardContent>
            </Card>
          )}

        </div>
      </div>
      
    </div>
  );
}
