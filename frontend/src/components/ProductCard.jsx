import React from 'react';
import { motion } from 'framer-motion';

export default function ProductCard({ product, onAddToCart }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex flex-col gap-2 min-w-[200px] max-w-[250px]"
    >
      <div className="text-4xl text-center py-4 bg-gray-50 rounded-lg">
        {product.image_emoji || product.emoji || '🛍️'}
      </div>
      <div>
        <h3 className="font-bold text-gray-900 truncate">{product.name}</h3>
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{product.category}</span>
      </div>
      <div className="text-lg font-bold text-[#0B69FF]">
        ₹{product.price?.toLocaleString()}
      </div>
      <p className="text-xs text-gray-500 line-clamp-2 min-h-[32px]">
        {product.description}
      </p>
      <div className="mt-2 flex flex-col gap-2">
        <button
          onClick={() => onAddToCart(product)}
          className="w-full bg-[#0B69FF] text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Add to Cart 🛒
        </button>
        <button className="w-full text-xs text-[#0B69FF] hover:underline py-1">
          View Details
        </button>
      </div>
    </motion.div>
  );
}
