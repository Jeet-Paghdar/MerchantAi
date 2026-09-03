import React from 'react';
import { motion } from 'framer-motion';

export default function MessageBubble({ message }) {
  const isAgent = message.role === 'agent';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col max-w-[80%] ${isAgent ? 'self-start' : 'self-end'}`}
    >
      <div
        className={`px-4 py-3 text-sm ${
          isAgent
            ? 'bg-white text-[#1a1a1a] rounded-2xl rounded-bl-sm shadow-sm'
            : 'bg-[#0B69FF] text-white rounded-2xl rounded-br-sm'
        }`}
      >
        {message.text}
      </div>
      <span className={`text-[10px] mt-1 text-gray-400 ${isAgent ? 'text-left ml-1' : 'text-right mr-1'}`}>
        {message.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </span>
    </motion.div>
  );
}
