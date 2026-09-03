import React from 'react';
import { motion } from 'framer-motion';

export default function RoleGateway({ onSelectRole }) {
  return (
    <div className="min-h-screen bg-[#072654] flex flex-col justify-center items-center p-6 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-[#0B69FF]/20 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-4xl w-full z-10">
        {/* Header Branding */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-white/10 px-4 py-1.5 rounded-full border border-white/15 mb-4 shadow-sm">
            <span className="text-xs font-bold text-white uppercase tracking-wider">Razorpay Agentic Commerce Track 01</span>
          </div>
          <div className="flex items-center justify-center gap-3 mb-2">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#0B69FF"/>
              <path d="M2 17L12 22L22 17" stroke="#0B69FF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="#0B69FF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">
              MerchantAI
            </h1>
          </div>
          <p className="text-gray-300 text-sm sm:text-base mt-3 max-w-xl mx-auto">
            Autonomous growth, conversational checkout, and machine-to-machine commerce infrastructure for e-commerce merchants.
          </p>
          <div className="mt-2 text-xs font-semibold text-[#528FF0]">
            Select an entry portal to begin the live demo
          </div>
        </div>

        {/* Role Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 1. Buyer Persona Card */}
          <motion.div 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.99 }}
            className="bg-white rounded-2xl p-8 shadow-xl flex flex-col justify-between border-2 border-transparent hover:border-[#0B69FF] transition-all cursor-pointer group"
            onClick={() => onSelectRole('buyer')}
          >
            <div>
              <div className="w-14 h-14 rounded-2xl bg-blue-50 flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform">
                🛍️
              </div>
              <div className="inline-block bg-blue-100 text-[#0B69FF] text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider mb-2">
                Customer Perspective
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Buyer Experience</h2>
              <p className="text-gray-500 text-xs sm:text-sm leading-relaxed mb-6">
                Browse the host store (<strong>TechBazaar</strong>), ask the embedded AI Shopping Copilot for recommendations, explore discounts, and complete native in-app checkout via Razorpay.
              </p>

              <div className="space-y-2 border-t border-gray-100 pt-4 mb-6">
                <div className="text-xs text-gray-600 flex items-center gap-2">
                  <span className="text-emerald-500 font-bold">✓</span> Real-time catalog search & cards
                </div>
                <div className="text-xs text-gray-600 flex items-center gap-2">
                  <span className="text-emerald-500 font-bold">✓</span> Conversational upsell & cross-sell
                </div>
                <div className="text-xs text-gray-600 flex items-center gap-2">
                  <span className="text-emerald-500 font-bold">✓</span> Explicit payment gate & Razorpay SDK
                </div>
              </div>
            </div>

            <button 
              className="w-full bg-[#0B69FF] hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl text-sm transition-all shadow-md group-hover:shadow-lg flex items-center justify-center gap-2"
            >
              <span>Enter Storefront as Shopper</span>
              <span>→</span>
            </button>
          </motion.div>

          {/* 2. Merchant Persona Card */}
          <motion.div 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.99 }}
            className="bg-[#0b172a] rounded-2xl p-8 shadow-xl flex flex-col justify-between border-2 border-white/10 hover:border-[#2DD589] transition-all cursor-pointer group"
            onClick={() => onSelectRole('merchant')}
          >
            <div>
              <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center text-3xl mb-6 group-hover:scale-110 transition-transform">
                💼
              </div>
              <div className="inline-block bg-emerald-500/20 text-[#2DD589] text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider mb-2">
                Store Owner Perspective
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Merchant Console</h2>
              <p className="text-gray-300 text-xs sm:text-sm leading-relaxed mb-6">
                Inspect AI-driven revenue gains, manage margin protection bounds (min 8% margin), run automated cart recovery campaigns, and monitor the compliance audit trail.
              </p>

              <div className="space-y-2 border-t border-white/10 pt-4 mb-6">
                <div className="text-xs text-gray-300 flex items-center gap-2">
                  <span className="text-[#2DD589] font-bold">✓</span> Revenue growth metrics & recovered carts
                </div>
                <div className="text-xs text-gray-300 flex items-center gap-2">
                  <span className="text-[#2DD589] font-bold">✓</span> Autonomous Agent Arena (x402 wire)
                </div>
                <div className="text-xs text-gray-300 flex items-center gap-2">
                  <span className="text-[#2DD589] font-bold">✓</span> Full Audit Trail (bounded & gated money actions)
                </div>
              </div>
            </div>

            <button 
              className="w-full bg-[#2DD589] hover:bg-emerald-600 text-[#072654] font-extrabold py-3.5 rounded-xl text-sm transition-all shadow-md group-hover:shadow-lg flex items-center justify-center gap-2"
            >
              <span>Open Merchant Command Center</span>
              <span>→</span>
            </button>
          </motion.div>
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center text-xs text-gray-400">
          Tip for judges: You can switch between portals anytime using the button in the top navigation bar.
        </div>
      </div>
    </div>
  );
}
