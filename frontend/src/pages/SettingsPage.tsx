import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, Trash2, TestTube, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { settingsApi } from "@/api/settings";

export function SettingsPage() {
  const qc = useQueryClient();
  const { data: config, isLoading } = useQuery({
    queryKey: ["ai-config"],
    queryFn: settingsApi.getAIConfig,
  });

  const [provider, setProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [orgId, setOrgId] = useState("");
  const [testResult, setTestResult] = useState<any>(null);

  // Initialize form when config loads
  useEffect(() => {
    if (config && !config.using_global_key) {
      setProvider(config.provider || "");
      setBaseUrl(config.base_url || "");
      setOrgId(config.organization_id || "");
    }
  }, [config]);

  const testMutation = useMutation({
    mutationFn: settingsApi.testAIConfig,
    onSuccess: (data) => setTestResult(data),
  });

  const updateMutation = useMutation({
    mutationFn: settingsApi.updateAIConfig,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ai-config"] });
      setApiKey(""); // Clear the API key input after save
      setTestResult({ success: true, message: "Settings saved successfully", error: null });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: settingsApi.deleteAIConfig,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["ai-config"] });
      setProvider("");
      setApiKey("");
      setBaseUrl("");
      setOrgId("");
      setTestResult(null);
    },
  });

  const handleTest = () => {
    if (!provider || !apiKey) {
      setTestResult({
        success: false,
        message: "Please select provider and enter API key",
        error: null,
      });
      return;
    }
    testMutation.mutate({ provider, api_key: apiKey, base_url: baseUrl || undefined });
  };

  const handleSave = () => {
    if (!provider || !apiKey) {
      setTestResult({
        success: false,
        message: "Provider and API key are required",
        error: null,
      });
      return;
    }
    updateMutation.mutate({
      provider,
      api_key: apiKey,
      base_url: baseUrl || undefined,
      organization_id: orgId || undefined,
    });
  };

  if (isLoading) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Configure your AI provider and API key
        </p>
      </div>

      <Card className="p-6">
        <div className="space-y-6">
          {/* Current Status */}
          {config?.using_global_key && (
            <div className="p-3 bg-muted rounded-lg">
              <p className="text-sm">
                You're currently using the global API key. Configure your own key below
                to use your preferred AI provider.
              </p>
            </div>
          )}

          {config?.api_key_masked && (
            <div className="p-3 bg-muted rounded-lg">
              <p className="text-sm font-medium">Current API Key</p>
              <p className="text-sm text-muted-foreground font-mono">
                {config.api_key_masked}
              </p>
            </div>
          )}

          {/* Provider Selection */}
          <div className="space-y-2">
            <Label htmlFor="provider">AI Provider</Label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger>
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openrouter">OpenRouter</SelectItem>
                <SelectItem value="openai">OpenAI</SelectItem>
                <SelectItem value="anthropic">Anthropic</SelectItem>
                <SelectItem value="custom">Custom</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <Label htmlFor="apiKey">API Key</Label>
            <Input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-..."
            />
            <p className="text-xs text-muted-foreground">
              Your API key is encrypted and never shown in plain text
            </p>
          </div>

          {/* Base URL (for custom provider) */}
          {provider === "custom" && (
            <div className="space-y-2">
              <Label htmlFor="baseUrl">Base URL</Label>
              <Input
                id="baseUrl"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="https://api.example.com/v1"
              />
            </div>
          )}

          {/* Organization ID (for OpenAI) */}
          {provider === "openai" && (
            <div className="space-y-2">
              <Label htmlFor="orgId">Organization ID (Optional)</Label>
              <Input
                id="orgId"
                value={orgId}
                onChange={(e) => setOrgId(e.target.value)}
                placeholder="org-..."
              />
            </div>
          )}

          {/* Test Result */}
          {testResult && (
            <div
              className={`p-3 rounded-lg flex items-start gap-2 ${
                testResult.success
                  ? "bg-green-50 text-green-900 border border-green-200"
                  : "bg-red-50 text-red-900 border border-red-200"
              }`}
            >
              {testResult.success ? (
                <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              ) : (
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              )}
              <div className="flex-1">
                <p className="text-sm font-medium">{testResult.message}</p>
                {testResult.error && (
                  <p className="text-xs mt-1 font-mono break-all">{testResult.error}</p>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <Button
              onClick={handleTest}
              variant="outline"
              disabled={!provider || !apiKey || testMutation.isPending}
            >
              <TestTube className="w-4 h-4 mr-2" />
              Test Connection
            </Button>
            <Button
              onClick={handleSave}
              disabled={!provider || !apiKey || updateMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              Save Settings
            </Button>
            {!config?.using_global_key && (
              <Button
                onClick={() => deleteMutation.mutate()}
                variant="destructive"
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Revert to Global Key
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}
