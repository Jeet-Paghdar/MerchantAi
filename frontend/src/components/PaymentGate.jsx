import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api';

export default function PaymentGate({ orderInfo, sessionId, onClose, onSuccess = () => {}, onFailure = () => {} }) {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      // Get real Razorpay Key ID from backend config
      const config = await api.getCheckoutConfig();
      const razorpayKey = config.razorpay_key_id || 'rzp_test_TXgh5Bw3BZhcbi';

      let razorpayOrderId = orderInfo.razorpay_order_id || orderInfo.razorpayOrderId;
      const amount = orderInfo.amount || orderInfo.total;
      
      if (!razorpayOrderId) {
        const orderData = await api.createOrder(sessionId);
        razorpayOrderId = orderData.razorpay_order_id;
      }

      const options = {
        key: razorpayKey,
        amount: Math.round(amount * 100),
        currency: 'INR',
        name: 'TechBazaar',
        description: 'MerchantAI In-App Checkout',
        order_id: razorpayOrderId,
        theme: { color: '#0B69FF' },
        handler: async function (response) {
          try {
            const verifyRes = await api.verifyPayment({
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature,
              session_id: sessionId
            });
            onSuccess('Payment successful! 🎉 Your order has been placed.');
          } catch (err) {
            onFailure('Payment verification failed.');
          }
        },
        modal: {
          ondismiss: function() {
            setLoading(false);
          }
        }
      };
      
      const rzp = new window.Razorpay(options);
      rzp.on('payment.failed', function (response){
        onFailure(`Payment failed: ${response.error.description}`);
      });
      rzp.open();
    } catch (err) {
      console.error(err);
      onFailure('Failed to initiate payment.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden"
      >
        <div className="bg-[#528FF0]/10 px-6 py-4 border-b border-[#528FF0]/20 flex items-center gap-2">
          <span className="text-xl">🔒</span>
          <span className="text-sm font-semibold text-[#072654]">
            GATE: This payment requires your explicit confirmation
          </span>
        </div>
        
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Order Summary</h2>
          
          <div className="space-y-4 mb-6 max-h-60 overflow-y-auto">
            {orderInfo.items?.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="text-gray-600">{item.name} x {item.quantity || 1}</span>
                <span className="font-medium">₹{item.price?.toLocaleString()}</span>
              </div>
            ))}
          </div>
          
          <div className="border-t border-gray-100 pt-4 mb-6 space-y-2">
            {orderInfo.subtotal && orderInfo.discount_percent > 0 && (
              <>
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>Subtotal</span>
                  <span>₹{orderInfo.subtotal?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center text-sm text-emerald-600 font-medium">
                  <span>Discount ({orderInfo.discount_percent}%)</span>
                  <span>-₹{orderInfo.discount_amount?.toLocaleString()}</span>
                </div>
              </>
            )}
            <div className="flex justify-between items-center pt-2 border-t border-dashed border-gray-200">
              <span className="font-bold text-gray-900">Final Payable Amount</span>
              <span className="text-2xl font-bold text-[#0B69FF]">
                ₹{(orderInfo.amount || orderInfo.total)?.toLocaleString()}
              </span>
            </div>
          </div>
          
          <div className="flex flex-col gap-3">
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="w-full bg-[#0B69FF] text-white py-3.5 rounded-xl font-bold text-lg hover:bg-blue-700 transition-colors disabled:opacity-70"
            >
              {loading ? 'Processing...' : `Confirm & Pay ₹${(orderInfo.amount || orderInfo.total)?.toLocaleString()}`}
            </button>
            <button
              onClick={onClose}
              disabled={loading}
              className="w-full text-gray-500 py-2 text-sm font-medium hover:text-gray-700 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
