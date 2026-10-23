"use client";
import React from "react";
import { TrendingUp, Database, AlertCircle, CheckCircle2, ArrowUpRight } from "lucide-react";

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Annual Recurring Revenue" value="$12.4M" change="+12.5%" icon={<TrendingUp className="text-emerald-500" />} />
        <StatCard title="Active Datasets" value="14" change="+2" icon={<Database className="text-brand-500" />} />
        <StatCard title="AI Data Quality" value="94.2%" change="-0.4%" icon={<CheckCircle2 className="text-brand-500" />} />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* AI Insights Panel */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
              <h3 className="text-lg font-semibold">Autonomous AI Insights</h3>
              <button className="text-sm text-brand-600 font-medium hover:underline flex items-center gap-1">
                View All <ArrowUpRight size={14}/>
              </button>
            </div>
            <div className="p-6 space-y-4">
              <InsightItem 
                type="recommendation" 
                title="Revenue Anomaly Detected" 
                desc="APAC region showed a 14% drop in revenue for Q3 compared to last year. AI suggests analyzing churn in the 'Enterprise' segment."
                status="High"
              />
              <InsightItem 
                type="cleaning" 
                title="Data Quality Alert" 
                desc="Dataset 'Global_Sales_2026' contains 120 null values in 'region'. AI suggests filling with 'UNKNOWN'."
                status="Medium"
              />
              <InsightItem 
                type="success" 
                title="Automated Pipeline Complete" 
                desc="The nightly ETL pipeline for Sales data finished successfully in 4m 12s."
                status="Info"
              />
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="text-md font-semibold mb-4">Governance Guard</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                <div className="flex items-center gap-3">
                  <AlertCircle size={18} className="text-amber-500" />
                  <span className="text-sm font-medium">Pending Approval</span>
                </div>
                <span className="text-xs font-bold text-amber-600 bg-amber-100 px-2 py-1 rounded">2 Requests</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                <div className="flex items-center gap-3">
                  <CheckCircle2 size={18} className="text-emerald-500" />
                  <span className="text-sm font-medium">Safe Operations</span>
                </div>
                <span className="text-xs font-bold text-emerald-600 bg-emerald-100 px-2 py-1 rounded">Active</span>
              </div>
            </div>
            <button className="w-full mt-6 py-2 bg-slate-900 text-white rounded-xl text-sm font-medium hover:bg-slate-800 transition-colors">
              Manage Approvals
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, change, icon }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-slate-50 rounded-lg">{icon}</div>
        <span className={`text-xs font-bold px-2 py-1 rounded ${change.startsWith('+') ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'}`}>
          {change}
        </span>
      </div>
      <p className="text-sm text-slate-500 font-medium">{title}</p>
      <h4 className="text-2xl font-bold text-slate-900">{value}</h4>
    </div>
  );
}

function InsightItem({ type, title, desc, status }) {
  const colors = {
    recommendation: "border-l-amber-500",
    cleaning: "border-l-brand-500",
    success: "border-l-emerald-500"
  };
  return (
    <div className={`p-4 bg-slate-50 rounded-xl border-l-4 ${colors[type] || "border-l-slate-300"} space-y-1`}>
      <div className="flex justify-between items-center">
        <span className="text-sm font-bold text-slate-800">{title}</span>
        <span className="text-[10px] uppercase font-bold text-slate-400">{status}</span>
      </div>
      <p className="text-sm text-slate-600 leading-relaxed">{desc}</p>
    </div>
  );
}
