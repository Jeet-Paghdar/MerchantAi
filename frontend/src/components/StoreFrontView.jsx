import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { motion, AnimatePresence } from 'framer-motion';
import PaymentGate from './PaymentGate';

export default function StoreFrontView({ sessionId, onOpenAssistant }) {
  const [products, setProducts] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [search, setSearch] = useState('');
  const [addedItemName, setAddedItemName] = useState(null);
  const [orderInfo, setOrderInfo] = useState(null);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    fetchProducts();
    fetchCart();
  }, []);

  const fetchProducts = async () => {
    try {
      const data = await api.getCatalog({});
      if (Array.isArray(data)) {
        setProducts(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchCart = async () => {
    try {
      const res = await api.getCart(sessionId);
      if (res && res.items) {
        const total = res.items.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        setCart({ items: res.items, total });
      }
    } catch (e) {
      // Cart might be empty initially
    }
  };

  const handleQuickAdd = async (product) => {
    try {
      await api.addToCart(sessionId, product.id, 1);
      setAddedItemName(product.name);
      setTimeout(() => setAddedItemName(null), 2500);
      fetchCart();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCheckout = async () => {
    if (cart.items.length === 0) return;
    setCheckoutLoading(true);
    try {
      const order = await api.createOrder(sessionId);
      setOrderInfo(order);
    } catch (err) {
      console.error(err);
    } finally {
      setCheckoutLoading(false);
    }
  };

  const categories = ['All', 'Phones', 'Audio', 'Laptops', 'Accessories'];

  const filteredProducts = products.filter(p => {
    const matchesCat = selectedCategory === 'All' || p.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchesSearch = !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.description.toLowerCase().includes(search.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="flex-1 flex flex-col bg-[#F8F9FA] overflow-y-auto">
      {/* Top Banner explaining this is a merchant's store */}
      <div className="bg-gradient-to-r from-[#072654] to-[#0B69FF] text-white px-6 py-2 text-xs flex justify-between items-center shadow-inner">
        <div className="flex items-center gap-2">
          <span className="bg-emerald-500 text-white font-bold px-2 py-0.5 rounded text-[10px] uppercase tracking-wider">Live Integration</span>
          <span>Merchant Store: <strong>TechBazaar Inc.</strong></span>
        </div>
        <div className="flex items-center gap-3">
          <span className="opacity-90">Embedded SDK: <strong>MerchantAI Copilot v1.0</strong></span>
          <span className="hidden sm:inline opacity-75">|</span>
          <span className="hidden sm:inline bg-white/20 px-2 py-0.5 rounded font-mono text-[11px]">Powered by Razorpay</span>
        </div>
      </div>

      {/* Hero Section */}
      <div className="px-8 py-8 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <span>Home</span> &gt; <span>Electronics & Lifestyle</span>
            </div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">TechBazaar Official Store</h1>
            <p className="text-gray-500 text-sm mt-1">
              Browse products below, or ask the <strong>MerchantAI Copilot</strong> at bottom right to find & negotiate deals!
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={() => onOpenAssistant("Show me the best deals today")}
              className="bg-gradient-to-r from-[#0B69FF] to-blue-600 text-white px-4 py-2.5 rounded-xl font-semibold text-sm shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer"
            >
              <span>✨ Ask AI Shopper</span>
            </button>
            <div className="bg-gray-100 border border-gray-200 rounded-xl px-4 py-2 flex items-center gap-2 text-sm font-bold text-gray-800">
              <span>🛒</span>
              <span>₹{cart.total.toLocaleString()}</span>
              {cart.items.length > 0 && (
                <span className="bg-[#0B69FF] text-white text-xs px-2 py-0.5 rounded-full font-bold">
                  {cart.items.reduce((a, b) => a + b.quantity, 0)}
                </span>
              )}
            </div>
            {cart.items.length > 0 && (
              <button
                onClick={handleCheckout}
                disabled={checkoutLoading}
                className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2.5 rounded-xl font-semibold text-sm shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer disabled:opacity-70"
              >
                {checkoutLoading ? '⏳ Processing...' : '💳 Checkout'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="max-w-6xl mx-auto w-full px-8 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mb-6">
          {/* Category Tabs */}
          <div className="flex overflow-x-auto gap-2 w-full sm:w-auto pb-2 sm:pb-0 scrollbar-hide">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-[#072654] text-white shadow-sm'
                    : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Search Input */}
          <div className="w-full sm:w-64">
            <input
              type="text"
              placeholder="Search store catalog..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm outline-none focus:border-[#0B69FF]"
            />
          </div>
        </div>

        {/* Added Notification Toast */}
        <AnimatePresence>
          {addedItemName && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-6 bg-emerald-50 border border-emerald-300 text-emerald-800 px-4 py-3 rounded-xl text-sm flex items-center justify-between"
            >
              <div className="flex items-center gap-2 font-medium">
                <span>✅</span> Added <strong>{addedItemName}</strong> to cart via MerchantAI!
              </div>
              <button 
                onClick={handleCheckout}
                className="text-xs font-bold text-emerald-900 underline ml-4 hover:opacity-80 cursor-pointer"
              >
                Go to Checkout →
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Product Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredProducts.map(p => (
            <div 
              key={p.id}
              className="bg-white rounded-2xl border border-gray-200 p-5 flex flex-col justify-between hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
            >
              <div>
                <div className="h-32 bg-gray-50 rounded-xl flex items-center justify-center text-5xl mb-4 border border-gray-100">
                  {p.image_emoji || '🛍️'}
                </div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#0B69FF] bg-blue-50 px-2 py-0.5 rounded">
                    {p.category}
                  </span>
                  <span className="text-xs text-gray-400">Stock: {p.stock}</span>
                </div>
                <h3 className="font-bold text-gray-900 text-base mb-1 truncate">{p.name}</h3>
                <p className="text-xs text-gray-500 line-clamp-2 mb-3">{p.description}</p>
              </div>

              <div>
                <div className="text-xl font-extrabold text-gray-900 mb-3">
                  ₹{p.price.toLocaleString()}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleQuickAdd(p)}
                    className="w-full bg-gray-900 hover:bg-black text-white text-xs font-bold py-2.5 rounded-lg transition-colors cursor-pointer"
                  >
                    Add to Cart
                  </button>
                  <button
                    onClick={() => onOpenAssistant(`Tell me more about ${p.name} and can I get a discount?`)}
                    className="w-full border border-gray-200 hover:border-[#0B69FF] hover:text-[#0B69FF] text-gray-600 text-xs font-semibold py-2.5 rounded-lg transition-colors cursor-pointer"
                  >
                    Ask AI 💬
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      {orderInfo && (
        <PaymentGate
          orderInfo={orderInfo}
          sessionId={sessionId}
          onClose={() => { setOrderInfo(null); fetchCart(); }}
        />
      )}
    </div>
  );
}
