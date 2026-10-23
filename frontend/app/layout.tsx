"use client";
import React from "react";
import "./globals.css";
import { LayoutDashboard, Database, MessageSquare, Settings, LogOut, Bell } from "lucide-react";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 font-sans">
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 bg-brand-900 text-white flex flex-col">
            <div className="p-6 flex items-center gap-3">
              <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center font-bold">A</div>
              <span className="text-lg font-semibold tracking-tight">AutoAnalytics</span>
            </div>
            
            <nav className="flex-1 px-4 space-y-2 mt-4">
              <NavItem icon={<LayoutDashboard size={20}/>} label="Dashboard" active />
              <NavItem icon={<Database size={20}/>} label="Datasets" />
              <NavItem icon={<MessageSquare size={20}/>} label="AI Chat" />
              <NavItem icon={<Settings size={20}/>} label="Settings" />
            </nav>

            <div className="p-4 border-t border-brand-800">
              <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-brand-800 cursor-pointer transition-colors">
                <div className="w-8 h-8 rounded-full bg-brand-400 flex items-center justify-center text-xs">PK</div>
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm font-medium truncate">Partner Demo</p>
                  <p className="text-xs text-brand-300 truncate">partner@demo.ai</p>
                </div>
                <LogOut size={16} className="text-brand-300" />
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 flex flex-col overflow-hidden">
            <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8">
              <h1 className="text-xl font-semibold text-slate-800">Enterprise Analytics</h1>
              <div className="flex items-center gap-4">
                <button className="p-2 text-slate-400 hover:text-slate-600 relative">
                  <Bell size={20} />
                  <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
                </button>
                <div className="h-8 w-px bg-slate-200 mx-2"></div>
                <span className="text-sm font-medium text-slate-600">Workspace: APAC-Global</span>
              </div>
            </header>
            <div className="flex-1 overflow-auto p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}

function NavItem({ icon, label, active = false }) {
  return (
    <div className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-all ${active ? 'bg-brand-600 text-white' : 'text-brand-300 hover:bg-brand-800 hover:text-white'}`}>
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}
