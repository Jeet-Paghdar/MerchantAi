import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';

export default function AuditTrail({ sessionId }) {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    if (!sessionId) return;
    
    const fetchTrail = async () => {
      try {
        const data = await api.getAuditTrail(sessionId);
        if (data && Array.isArray(data)) {
          setEntries(data);
        } else if (data && data.logs) {
          setEntries(data.logs);
        } else if (data && data.trail) {
          setEntries(data.trail);
        }
      } catch (err) {
        console.error("Failed to fetch audit trail", err);
      }
    };
    
    fetchTrail();
    const interval = setInterval(fetchTrail, 3000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const getBorderColor = (type, status) => {
    if (status === 'success') return 'border-l-[#2DD589]';
    if (status === 'failure' || status === 'error') return 'border-l-[#E74C3C]';
    if (type === 'GATE_CHECK' || status === 'waiting') return 'border-l-[#528FF0]';
    if (type === 'BOUNDS_CHECK' && status === 'exceeded') return 'border-l-yellow-500';
    return 'border-l-[#0B69FF]';
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="p-4 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-white z-10">
        <h2 className="font-bold text-[#072654] flex items-center gap-2">
          📋 Audit Trail
        </h2>
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <div className="w-2 h-2 rounded-full bg-[#2DD589] animate-pulse" />
          Live
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        {entries.length === 0 ? (
          <div className="text-sm text-gray-400 text-center mt-10">No audit events yet.</div>
        ) : (
          entries.map((entry, i) => (
            <motion.div
              key={entry.id || i}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`bg-white rounded-lg shadow-sm border border-gray-100 border-l-4 p-3 text-sm ${getBorderColor(entry.type, entry.status)}`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-bold text-[#072654] text-xs uppercase tracking-wider">{entry.action_type || entry.type || entry.action}</span>
                <span className="text-[10px] text-gray-400 font-mono">
                  {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
              <p className="text-gray-600 text-xs mt-1 leading-relaxed">{entry.reasoning || entry.details}</p>
              
              <div className="flex flex-wrap gap-1.5 mt-2">
                {entry.bounds_check && (
                  <span className={`text-[10px] px-2 py-0.5 rounded font-semibold ${
                    entry.bounds_check.passed ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-700'
                  }`}>
                    {entry.bounds_check.passed ? 'BOUNDS PASS ✓' : 'BOUNDS EXCEEDED ✗'}
                  </span>
                )}
                
                {entry.gate_check && (
                  <span className="text-[10px] px-2 py-0.5 rounded font-semibold bg-blue-100 text-blue-800">
                    GATE CONFIRMED 🔒
                  </span>
                )}
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
