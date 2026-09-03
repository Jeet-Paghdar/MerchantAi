import React, { useState, useEffect } from 'react';
import StoreFrontView from './components/StoreFrontView';
import ChatWindow from './components/ChatWindow';
import ArenaView from './components/ArenaView';
import CampaignDash from './components/CampaignDash';
import AuditTrail from './components/AuditTrail';
import RoleGateway from './components/RoleGateway';
import { api } from './api';

function OrderList() {
  const [orders, setOrders] = useState([]);
  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getOrders();
        if (Array.isArray(data)) setOrders(data);
      } catch (e) {}
    };
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  if (orders.length === 0) {
    return <div className="text-gray-400 text-xs py-8 text-center">No orders created yet. Complete a buyout to see it appear here!</div>;
  }

  return (
    <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
      {orders.map((o) => (
        <div key={o.id} className="p-3 bg-gray-50 border border-gray-100 rounded-xl text-xs flex justify-between items-center">
          <div>
            <div className="font-mono text-gray-700 font-bold">{o.razorpay_order_id}</div>
            <div className="text-gray-400 text-[10px] mt-0.5">
              {o.created_at ? new Date(o.created_at).toLocaleTimeString() : 'Just now'}
            </div>
          </div>
          <div className="text-right">
            <div className="font-bold text-emerald-600 text-sm">₹{o.amount?.toLocaleString()}</div>
            <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
              o.status === 'paid' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
            }`}>
              {o.status}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

function App() {
  const [portalMode, setPortalMode] = useState('gateway'); // 'gateway' | 'buyer' | 'merchant'
  const [activeTab, setActiveTab] = useState('store');
  const [sessionId, setSessionId] = useState('');
  const [prefilledMessage, setPrefilledMessage] = useState(null);

  useEffect(() => {
    // Generate simple UUID-like string for session
    const id = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    setSessionId(id);
  }, []);

  const handleSelectRole = (role) => {
    setPortalMode(role);
    if (role === 'buyer') {
      setActiveTab('store');
    } else {
      setActiveTab('campaigns');
    }
  };

  const buyerNavItems = [
    { id: 'store', label: 'Storefront' },
    { id: 'chat', label: 'AI Copilot Widget' }
  ];

  const merchantNavItems = [
    { id: 'campaigns', label: 'Revenue & Campaigns' },
    { id: 'arena', label: 'Agent Arena (x402)' },
    { id: 'audit', label: 'Settled Orders & Audit' }
  ];

  if (portalMode === 'gateway') {
    return <RoleGateway onSelectRole={handleSelectRole} />;
  }

  const currentNavItems = portalMode === 'buyer' ? buyerNavItems : merchantNavItems;

  return (
    <div className="h-screen flex flex-col bg-[#F8F9FA] overflow-hidden">
      <header className="bg-[#072654] text-white px-6 py-3 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#0B69FF"/>
              <path d="M2 17L12 22L22 17" stroke="#0B69FF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="#0B69FF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span className="text-xl font-bold tracking-tight">MerchantAI</span>
          </div>
          <span className="text-xs text-[#0B69FF] font-medium hidden sm:inline ml-2">Powered by Razorpay</span>

          {/* Persona indicator pill */}
          <div className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5 ${
            portalMode === 'buyer' ? 'bg-blue-500/20 text-blue-300 border border-blue-400/30' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30'
          }`}>
            <span>{portalMode === 'buyer' ? '👤 Customer Mode' : '💼 Merchant Console'}</span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <nav className="flex gap-4">
            {currentNavItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`pb-1 px-1 font-semibold text-xs sm:text-sm transition-colors duration-200 cursor-pointer ${
                  activeTab === item.id 
                    ? 'text-white border-b-2 border-[#0B69FF]' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* Quick Switch Role Button */}
          <button
            onClick={() => handleSelectRole(portalMode === 'buyer' ? 'merchant' : 'buyer')}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 shadow-sm"
          >
            <span>⇄</span>
            <span>Switch to {portalMode === 'buyer' ? 'Merchant' : 'Shopper'}</span>
          </button>
        </div>
      </header>

      <main className="flex-1 flex flex-col overflow-hidden">
        {sessionId ? (
          <>
            {activeTab === 'store' && (
              <StoreFrontView 
                sessionId={sessionId} 
                onOpenAssistant={(msg) => {
                  setPrefilledMessage(msg);
                  setActiveTab('chat');
                }} 
              />
            )}
            {activeTab === 'chat' && <ChatWindow sessionId={sessionId} initialInput={prefilledMessage} />}
            {activeTab === 'arena' && <ArenaView />}
            {activeTab === 'campaigns' && <CampaignDash />}
            {activeTab === 'audit' && (
              <div className="p-8 flex-1 overflow-y-auto bg-[#F8F9FA] max-w-6xl mx-auto w-full">
                <div className="mb-6">
                  <h1 className="text-2xl font-extrabold text-[#072654]">Order History & Compliance Audit Trail</h1>
                  <p className="text-xs text-gray-500 mt-1">Review all completed buyouts, Razorpay order IDs, and real-time agent audit logs.</p>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
                    <h2 className="font-bold text-gray-900 mb-4 flex items-center justify-between text-sm uppercase tracking-wider">
                      <span>📦 Settled Orders</span>
                      <span className="text-xs text-emerald-600 font-semibold">Live DB</span>
                    </h2>
                    <OrderList />
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
                    <AuditTrail sessionId={sessionId} />
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center h-full">Loading session...</div>
        )}
      </main>
    </div>
  );
}

export default App;
