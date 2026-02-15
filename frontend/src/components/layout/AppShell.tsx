import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function AppShell() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 min-h-0 flex flex-col p-6">
          <div className="flex-1 min-h-0 overflow-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
