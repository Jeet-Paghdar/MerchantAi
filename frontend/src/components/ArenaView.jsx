import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';

export default function ArenaView() {
  const [task, setTask] = useState('Buy me the best phone under ₹15,000');
  const [isRunning, setIsRunning] = useState(false);
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState(null); // 'success' | 'failed'
  const [result, setResult] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleStart = async () => {
    if (!task) return;
    setIsRunning(true);
    setMessages([]);
    setStatus(null);
    setResult(null);

    try {
      // Call start API
      await api.startArena(task);
      
      // Simulate real-time by polling or hitting simulate endpoint
      // Assuming simulateArena returns an array of events/messages over time or we poll it
      // For this example, let's assume it streams or we do a one-off that returns full log and we simulate locally
      const response = await api.simulateArena(task);
      const events = response.events || [];
      
      // Simulate typing delay
      for (let i = 0; i < events.length; i++) {
        await new Promise(r => setTimeout(r, 1000 + Math.random() * 1000));
        setMessages(prev => [...prev, events[i]]);
      }
      
      if (response.status === 'success') {
        setStatus('success');
        setResult(response.result);
      } else {
        setStatus('failed');
        setResult(response.result);
      }
    } catch (err) {
      console.error(err);
      setStatus('failed');
      setResult({ reason: 'Simulation failed to complete.' });
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#F8F9FA] p-6 max-w-6xl mx-auto w-full">
      <div className="bg-white p-4 rounded-xl shadow-sm mb-6 flex gap-4 items-center">
        <input
          type="text"
          value={task}
          onChange={e => setTask(e.target.value)}
          placeholder="Enter a task for the buyer agent..."
          className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 outline-none focus:border-[#0B69FF]"
          disabled={isRunning}
        />
        <button
          onClick={handleStart}
          disabled={isRunning}
          className="bg-[#0B69FF] text-white px-6 py-3 rounded-lg font-bold disabled:opacity-50 hover:bg-blue-700 transition-colors whitespace-nowrap"
        >
          {isRunning ? 'Running...' : 'Start Arena 🏟️'}
        </button>
      </div>

      <div className="flex-1 flex gap-4 min-h-0">
        {/* Buyer Panel */}
        <div className="flex-1 bg-blue-50/50 rounded-xl border border-blue-100 flex flex-col overflow-hidden">
          <div className="bg-[#0B69FF] text-white p-3 font-bold text-center">Buyer Agent</div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
            {messages.filter(m => (m.agent === 'buyer' || m.sender === 'buyer')).map((msg, i) => (
              <motion.div initial={{opacity:0,x:-10}} animate={{opacity:1,x:0}} key={i} className="bg-white p-3 rounded-lg shadow-sm border border-blue-100 text-sm">
                {msg.thinking && <div className="text-gray-400 italic text-xs mb-2">💭 Thinking: {msg.thinking}</div>}
                <div>{msg.text}</div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Wire */}
        <div className="w-20 flex flex-col items-center justify-center text-gray-400 text-center px-1">
          <div className="text-[10px] font-bold uppercase tracking-wider bg-blue-100 text-[#0B69FF] px-2 py-1 rounded mb-2">
            ⚡ Wire
          </div>
          <div className="text-[11px] text-gray-500 font-mono text-center leading-tight">
            x402 / UAP Protocol
          </div>
        </div>

        {/* Seller Panel */}
        <div className="flex-1 bg-[#072654]/5 rounded-xl border border-[#072654]/10 flex flex-col overflow-hidden">
          <div className="bg-[#072654] text-white p-3 font-bold text-center">Seller Agent</div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
            {messages.filter(m => (m.agent === 'seller' || m.sender === 'seller' || m.sender === 'wire')).map((msg, i) => (
              <motion.div initial={{opacity:0,x:10}} animate={{opacity:1,x:0}} key={i} className={`p-3 rounded-lg shadow-sm text-sm ${msg.sender === 'wire' ? 'bg-emerald-50 border border-emerald-200 text-emerald-900 font-mono text-xs' : 'bg-white border border-[#072654]/10'}`}>
                {msg.thinking && <div className="text-gray-400 italic text-xs mb-2">💭 Thinking: {msg.thinking}</div>}
                <div>{msg.text}</div>
              </motion.div>
            ))}
            <div ref={scrollRef} />
          </div>
        </div>
      </div>

      {status === 'success' && (
        <motion.div initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} className="mt-6 bg-[#2DD589] text-white p-4 rounded-xl shadow-md text-center font-bold text-lg">
          ✅ {typeof result === 'string' ? result : `DEAL CLOSED — ₹${result?.amount?.toLocaleString() || '12,200'} via Razorpay`}
        </motion.div>
      )}
      {status === 'failed' && (
        <motion.div initial={{opacity:0,y:20}} animate={{opacity:1,y:0}} className="mt-6 bg-[#E74C3C] text-white p-4 rounded-xl shadow-md text-center font-bold text-lg">
          ❌ DEAL FAILED — {result?.reason || 'Agents could not reach an agreement.'}
        </motion.div>
      )}
    </div>
  );
}
