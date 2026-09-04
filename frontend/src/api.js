export const api = {
  sendMessage: async (sessionId, message) => {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message })
    });
    return res.json();
  },
  getCatalog: async (params) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/catalog?${query}`);
    return res.json();
  },
  getCheckoutConfig: async () => {
    const res = await fetch('/api/checkout/config');
    return res.json();
  },
  createOrder: async (sessionId) => {
    const res = await fetch('/api/checkout/create-order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
    return res.json();
  },
  verifyPayment: async (data) => {
    const res = await fetch('/api/checkout/verify-payment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },
  getOrders: async () => {
    const res = await fetch('/api/checkout/orders');
    return res.json();
  },
  getAuditTrail: async (sessionId) => {
    const res = await fetch(`/api/audit/trail?session_id=${sessionId}`);
    return res.json();
  },
  getCampaignDashboard: async () => {
    const res = await fetch('/api/campaigns/dashboard');
    return res.json();
  },
  triggerRecovery: async () => {
    const res = await fetch('/api/campaigns/trigger-recovery', { method: 'POST' });
    return res.json();
  },
  startArena: async (task) => {
    const res = await fetch('/api/arena/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task })
    });
    return res.json();
  },
  simulateArena: async (task) => {
    const res = await fetch(`/api/arena/simulate?task=${encodeURIComponent(task)}`);
    return res.json();
  },
  getCart: async (sessionId) => {
    const res = await fetch(`/api/checkout/cart/?session_id=${sessionId}`);
    return res.json();
  },
  addToCart: async (sessionId, productId, quantity = 1) => {
    const res = await fetch('/api/checkout/cart/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, product_id: productId, quantity })
    });
    return res.json();
  }
};
