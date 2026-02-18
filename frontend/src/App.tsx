import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "sonner";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppShell } from "@/components/layout/AppShell";
import { HomePage } from "@/pages/HomePage";
import { GoalTemplateSelectionPage } from "@/pages/GoalTemplateSelectionPage";
import { GoalDetailPage } from "@/pages/GoalDetailPage";
import { CoachingPage } from "@/pages/CoachingPage";
import { HabitsPage } from "@/pages/HabitsPage";
import { TrackersPage } from "@/pages/TrackersPage";
import { ProgressPage } from "@/pages/ProgressPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { AdminDashboard } from "@/pages/AdminDashboard";
import { LoginPage } from "@/pages/LoginPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || ""}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <TooltipProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route element={<ProtectedRoute />}>
                  <Route element={<AppShell />}>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/admin" element={<AdminDashboard />} />
                    <Route path="/goals/new" element={<GoalTemplateSelectionPage />} />
                    <Route path="/goals/:id" element={<GoalDetailPage />} />
                    <Route path="/goals/:id/coach" element={<CoachingPage />} />
                    <Route path="/habits" element={<HabitsPage />} />
                    <Route path="/trackers" element={<TrackersPage />} />
                    <Route path="/progress" element={<ProgressPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                  </Route>
                </Route>
              </Routes>
              <Toaster />
            </BrowserRouter>
          </TooltipProvider>
        </AuthProvider>
      </QueryClientProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
