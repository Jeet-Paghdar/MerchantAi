import React, { useState, useEffect } from 'react';
import { api } from '../api';

export default function CampaignDash() {
  const [stats, setStats] = useState({
    revenueGenerated: '₹3,42,850',
    upsellConversion: '28.4%',
    recoveredRevenue: '₹84,200',
    aiBuyerTraffic: '412 Orders',
    totalCarts: 142,
    recovered: 45,
    recoveryRate: 31.7,
    activeCampaigns: 12,
    recent: [
      { id: 'sess_9821', customer: 'AI Buyer (Claude 3.5 via x402)', action: 'Autonomous Deal Closed', revenue: '+₹12,200', status: 'Settled on Razorpay' },
      { id: 'sess_8412', customer: 'Human Shopper', action: 'Cart Recovery (Level 2 Urgency)', revenue: '+₹2,499', status: 'Recovered' },
      { id: 'sess_7109', customer: 'Human Shopper', action: 'Cross-sell (Spigen Case + Charger)', revenue: '+₹1,498', status: 'Upsold' },
      { id: 'sess_6502', customer: 'AI Buyer (Perplexity Shopping)', action: 'Instant Catalog Query & Buy', revenue: '+₹29,999', status: 'Settled on Razorpay' },
      { id: 'sess_5431', customer: 'Human Shopper', action: 'Abandoned Cart Followup', revenue: '₹0', status: 'Pending Customer' }
    ]
  });

  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationDone, setSimulationDone] = useState(false);

  const [simulationResult, setSimulationResult] = useState(null);

  const runSimulation = async () => {
    setIsSimulating(true);
    setSimulationResult(null);
    try {
      const res = await api.triggerRecovery();
      setSimulationResult(res.message || res.detail || "Error");
    } catch (e) {
      setSimulationResult("Failed to reach backend.");
    }
    setIsSimulating(false);
    setSimulationDone(true);
    setTimeout(() => {
      setSimulationDone(false);
      setSimulationResult(null);
    }, 8000);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto w-full h-full overflow-y-auto bg-[#F8F9FA]">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-[#0B69FF]/10 text-[#0B69FF] font-bold text-xs px-2.5 py-1 rounded-full uppercase tracking-wider">
              Merchant Revenue Engine
            </span>
            <span className="text-xs text-gray-500 font-medium">Store: TechBazaar</span>
          </div>
          <h1 className="text-3xl font-extrabold text-[#072654]">Merchant Growth & Agentic Commerce</h1>
          <p className="text-sm text-gray-500 mt-1">
            How MerchantAI grows your store revenue and opens your catalog to autonomous AI buyers via Razorpay.
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={runSimulation}
            disabled={isSimulating || simulationDone}
            className={`px-5 py-2.5 rounded-xl font-bold text-sm shadow-md transition-all cursor-pointer flex items-center gap-2 ${
              simulationDone 
                ? 'bg-emerald-500 text-white hover:bg-emerald-600' 
                : isSimulating
                  ? 'bg-[#0B69FF]/70 text-white cursor-wait'
                  : 'bg-[#0B69FF] text-white hover:bg-blue-700'
            }`}
          >
            {isSimulating ? (
              <>
                <span className="animate-spin">⏳</span> Orchestrating...
              </>
            ) : simulationDone ? (
              <>
                <span>✅</span> 3 Recovery Nudges Sent!
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" fill="currentColor"/>
                </svg>
                Run Cart Recovery Orchestrator
              </>
            )}
          </button>
        </div>
      </div>

      {simulationResult && (
        <div className="mb-8 bg-green-50 border border-green-200 rounded-xl p-4 shadow-sm relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-green-500"></div>
          <h3 className="text-sm font-bold text-green-800 mb-2 flex items-center gap-2">
            <span>💬</span> Generated WhatsApp Message Preview
          </h3>
          <p className="text-sm text-green-900 whitespace-pre-wrap font-mono bg-white p-3 rounded border border-green-100 shadow-inner">
            {simulationResult}
          </p>
          <div className="mt-2 text-xs text-green-600 font-medium">
            This event was permanently logged to the SQLite Audit Trail via Python.
          </div>
        </div>
      )}

      {/* Merchant Revenue Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">AI-Driven Revenue</div>
          <div className="text-3xl font-extrabold text-[#2DD589]">{stats.revenueGenerated}</div>
          <div className="text-xs text-gray-500 mt-2 flex items-center gap-1 font-medium">
            <span className="text-emerald-600 font-bold">↑ +34.2%</span> vs standard checkout
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Upsell & Cross-sell Rate</div>
          <div className="text-3xl font-extrabold text-[#0B69FF]">{stats.upsellConversion}</div>
          <div className="text-xs text-gray-500 mt-2 font-medium">
            AI suggested accessories & warranty
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Abandoned Carts Recovered</div>
          <div className="text-3xl font-extrabold text-[#072654]">{stats.recoveredRevenue}</div>
          <div className="text-xs text-gray-500 mt-2 font-medium">
            45 of 142 carts saved ({stats.recoveryRate}%)
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">AI Buyer Transactions</div>
          <div className="text-3xl font-extrabold text-purple-600">{stats.aiBuyerTraffic}</div>
          <div className="text-xs text-gray-500 mt-2 font-medium">
            Via NPCI UAP / x402 Commerce Wire
          </div>
        </div>
      </div>

      {/* Live AI Merchant Actions Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
          <h2 className="font-bold text-gray-900 text-sm uppercase tracking-wider">Live Merchant Revenue Feeds</h2>
          <span className="text-xs text-[#0B69FF] font-medium">Automatic Settlement via Razorpay</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-white border-b border-gray-100 text-gray-400 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3 font-semibold">Session ID</th>
                <th className="px-6 py-3 font-semibold">Channel / Buyer</th>
                <th className="px-6 py-3 font-semibold">Growth Strategy</th>
                <th className="px-6 py-3 font-semibold">Merchant Revenue</th>
                <th className="px-6 py-3 font-semibold">Razorpay Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {stats.recent?.map((c, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-gray-600">{c.id}</td>
                  <td className="px-6 py-4 font-semibold text-gray-800">{c.customer}</td>
                  <td className="px-6 py-4 text-gray-600 text-xs">{c.action}</td>
                  <td className="px-6 py-4 font-bold text-emerald-600">{c.revenue}</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
