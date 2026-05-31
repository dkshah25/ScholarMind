"use client";

import React, { useState } from "react";
import {
  LayoutDashboard,
  BookOpen,
  Cpu,
  Network,
  Beaker,
  FileText,
  PlusCircle,
  FolderLock,
  ChevronDown
} from "lucide-react";

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  sessions: any[];
  currentSession: any;
  onSelectSession: (session: any) => void;
  onCreateSession: (topic: string) => void;
}

export default function Sidebar({
  currentTab,
  setCurrentTab,
  sessions,
  currentSession,
  onSelectSession,
  onCreateSession
}: SidebarProps) {
  const [showDropdown, setShowDropdown] = useState(false);
  const [newTopic, setNewTopic] = useState("");
  const [showNewInput, setShowNewInput] = useState(false);

  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "workspace", label: "Research Workspace", icon: BookOpen },
    { id: "agents", label: "Agent Control Center", icon: Cpu },
    { id: "graph", label: "Knowledge Graph", icon: Network },
    { id: "experiments", label: "Experiments", icon: Beaker },
    { id: "reports", label: "Publication Reports", icon: FileText }
  ];

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTopic.trim()) {
      onCreateSession(newTopic.trim());
      setNewTopic("");
      setShowNewInput(false);
    }
  };

  return (
    <aside className="w-68 bg-slate-900/60 backdrop-blur-xl border-r border-white/5 flex flex-col h-screen text-slate-300 select-none">
      {/* Brand Header */}
      <div className="p-6 border-b border-white/5 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-teal-400 to-indigo-500 flex items-center justify-center font-bold text-white shadow-lg active-pulse">
          S
        </div>
        <div>
          <h1 className="font-bold text-white tracking-wider text-base">ScholarMind</h1>
          <span className="text-[10px] uppercase text-teal-400 font-semibold tracking-widest">Research OS v1.0</span>
        </div>
      </div>

      {/* Session Selector / Memory Manager */}
      <div className="p-4 border-b border-white/5">
        <label className="text-[10px] uppercase text-slate-500 font-bold tracking-wider block mb-2 px-1">
          Active Session
        </label>

        {/* Drodown Button */}
        <div className="relative">
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            className="w-full bg-slate-800/40 hover:bg-slate-800/80 border border-white/5 px-3 py-2.5 rounded-lg flex items-center justify-between text-left text-xs text-white font-medium glass-card-hover cursor-pointer"
          >
            <span className="truncate">
              {currentSession ? currentSession.topic : "Select or create session..."}
            </span>
            <ChevronDown size={14} className={`text-slate-400 transition-transform duration-200 ${showDropdown ? 'rotate-180' : ''}`} />
          </button>

          {showDropdown && (
            <div className="absolute top-full left-0 right-0 mt-1.5 bg-slate-950/95 backdrop-blur-2xl border border-white/10 rounded-lg shadow-2xl z-50 py-1.5 max-h-56 overflow-y-auto">
              {sessions.map((sess) => (
                <button
                  key={sess.id}
                  onClick={() => {
                    onSelectSession(sess);
                    setShowDropdown(false);
                  }}
                  className={`w-full text-left px-3 py-2 text-xs hover:bg-white/5 flex flex-col gap-0.5 border-b border-white/5 last:border-0 ${currentSession?.id === sess.id ? 'text-teal-400 bg-white/5' : 'text-slate-300'}`}
                >
                  <span className="font-semibold truncate">{sess.topic}</span>
                  <span className="text-[9px] text-slate-500">ID: {sess.id} | {sess.papers?.length || 0} papers</span>
                </button>
              ))}

              <button
                onClick={() => {
                  setShowNewInput(!showNewInput);
                  setShowDropdown(false);
                }}
                className="w-full text-left px-3 py-2.5 text-xs text-teal-400 hover:bg-teal-500/10 font-medium flex items-center gap-2"
              >
                <PlusCircle size={14} />
                <span>Create New Session</span>
              </button>
            </div>
          )}
        </div>

        {/* Create Input Field */}
        {showNewInput && (
          <form onSubmit={handleCreateSubmit} className="mt-3 flex gap-2">
            <input
              type="text"
              placeholder="E.g., Quantum ML Gaps"
              value={newTopic}
              onChange={(e) => setNewTopic(e.target.value)}
              className="bg-slate-950 border border-white/10 text-xs px-2 py-1.5 rounded-md text-white w-full focus:outline-none focus:border-teal-400"
            />
            <button
              type="submit"
              className="bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold px-2 py-1.5 rounded-md text-xs cursor-pointer"
            >
              Add
            </button>
          </form>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 flex flex-col gap-1.5 overflow-y-auto">
        <label className="text-[10px] uppercase text-slate-500 font-bold tracking-wider px-2 mb-1 block">
          Operating Modules
        </label>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              disabled={!currentSession}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg text-left text-xs font-semibold tracking-wide transition-all cursor-pointer ${isActive
                  ? "bg-gradient-to-r from-teal-500/15 to-indigo-500/5 text-white border-l-2 border-teal-400 shadow-md font-bold"
                  : currentSession
                    ? "hover:bg-white/5 hover:text-white"
                    : "opacity-40 cursor-not-allowed"
                }`}
            >
              <Icon size={16} className={isActive ? "text-teal-400" : "text-slate-400"} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Branding */}
      <div className="p-4 border-t border-white/5 text-[10px] text-slate-500 flex items-center gap-2 justify-center">
        <FolderLock size={12} className="text-slate-600" />
        <span>Hybrid SQLite & Supabase Memory</span>
        <span>Developed by Dharmit Shah</span>
      </div>
    </aside>
  );
}
