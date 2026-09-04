import React, { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import MessageBubble from './MessageBubble';
import ProductCard from './ProductCard';
import TypingIndicator from './TypingIndicator';
import PaymentGate from './PaymentGate';
import { motion } from 'framer-motion';

export default function ChatWindow({ sessionId, initialInput = null }) {
  const [messages, setMessages] = useState([
    { 
      role: 'agent', 
      text: '👋 Welcome to TechBazaar! I am the MerchantAI Copilot embedded on this store. Ask me about any product, discounts, or say "proceed to payment" when ready.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    }
  ]);
  const [input, setInput] = useState(initialInput || '');
  const [isTyping, setIsTyping] = useState(false);
  const [orderInfo, setOrderInfo] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (initialInput) {
      setInput(initialInput);
    }
  }, [initialInput]);

  const quickPrompts = [
    "📱 Find me a phone under ₹15,000",
    "🔋 Suggest a good powerbank",
    "🎧 Best headphones for music?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', text: input, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await api.sendMessage(sessionId, userMsg.text);
      const agentMsg = {
        role: 'agent',
        text: response.message || response.text || 'Done.',
        products: response.products,
        cartUpdate: response.cartUpdate || response.cart_update,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, agentMsg]);
      
      const orderData = response.orderInfo || response.order_info || response.checkout;
      if (orderData) {
        setOrderInfo(orderData);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'agent', text: 'Sorry, I encountered an error.', timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleAddToCart = async (product) => {
    const text = `Add ${product.name} to cart`;
    const userMsg = { role: 'user', text, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);
    
    try {
      const response = await api.sendMessage(sessionId, text);
      setMessages(prev => [...prev, {
        role: 'agent',
        text: response.message || response.text || `Added ${product.name} to your cart.`,
        cartUpdate: response.cartUpdate || response.cart_update,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
      const orderData = response.orderInfo || response.order_info || response.checkout;
      if (orderData) {
        setOrderInfo(orderData);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex-1 flex h-full w-full">
      <div className="flex-1 flex flex-col bg-[#072654] relative">
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
          {messages.map((msg, idx) => (
            <div key={idx} className="flex flex-col gap-2">
              <MessageBubble message={msg} />
              
              {msg.products && msg.products.length > 0 && (
                <div className="flex overflow-x-auto gap-4 py-2 pb-4 scrollbar-hide">
                  {msg.products.map(p => (
                    <ProductCard key={p.id || p.name} product={p} onAddToCart={handleAddToCart} />
                  ))}
                </div>
              )}
              
              {msg.cartUpdate && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-[#0B69FF]/20 border border-[#0B69FF]/30 text-white rounded-lg p-3 text-sm self-start max-w-[80%]"
                >
                  🛒 Cart updated: {msg.cartUpdate.items} items. Subtotal: ₹{msg.cartUpdate.total}
                </motion.div>
              )}
            </div>
          ))}
          {isTyping && (
            <div className="self-start">
              <TypingIndicator />
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="p-4 bg-[#072654] border-t border-white/10">
          {/* Quick Prompt Chips */}
          <div className="flex flex-wrap gap-2 max-w-4xl mx-auto mb-3">
            {quickPrompts.map((qp, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInput(qp.replace(/^[^\w\s]+\s*/, ''));
                }}
                className="text-xs bg-white/10 hover:bg-[#0B69FF]/40 text-white/90 border border-white/15 px-3 py-1.5 rounded-full transition-all duration-150 cursor-pointer shadow-sm"
              >
                {qp}
              </button>
            ))}
          </div>

          <div className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything, e.g. 'Find me a phone under ₹15,000' or 'Best wireless earbuds'..."
              className="flex-1 bg-white/10 text-white placeholder-white/50 rounded-full px-6 py-3 outline-none focus:ring-2 focus:ring-[#0B69FF]"
            />
            <button
              onClick={handleSend}
              className="bg-[#0B69FF] text-white px-6 py-3 rounded-full font-medium hover:bg-blue-600 transition-colors"
            >
              Send
            </button>
          </div>
          <div className="text-center mt-2">
            <span className="text-xs text-white/40">Powered by Razorpay ⚡</span>
          </div>
        </div>
      </div>
      

      {orderInfo && (
        <PaymentGate 
          orderInfo={orderInfo} 
          sessionId={sessionId} 
          onClose={() => setOrderInfo(null)} 
          onSuccess={(msg) => {
            setOrderInfo(null);
            setMessages(prev => [...prev, { role: 'agent', text: msg, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
          }}
          onFailure={(msg) => {
            setOrderInfo(null);
            setMessages(prev => [...prev, { role: 'agent', text: msg, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
          }}
        />
      )}
    </div>
  );
}
