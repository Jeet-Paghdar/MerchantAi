# MerchantAI ?
### Autonomous Agentic Commerce Engine for Razorpay (Track 01)

> **Built for Razorpay AI Hackathon (Track 01: Agentic Commerce)**  
> ?? **Live Demo:** [https://merchantai.onrender.com](https://merchantai.onrender.com)  
> ?? **5-Minute Video Walkthrough:** [Your Video Link Here]

---

## ?? Executive Summary

Razorpay is the backbone of Indian e-commerce. However, merchants lose **70% of potential sales** to abandoned carts, struggle to increase **Average Order Value (AOV)**, and are completely unprepared for the upcoming shift toward **autonomous AI-driven machine commerce (NPCI UAP / x402 protocol)**.

**MerchantAI** is an embeddable B2B Agentic Commerce engine that turns any merchant store into an intelligent, autonomous commerce hub. It increases merchant revenue through conversational upsell and automated recovery campaigns, while strictly enforcing **hardcoded programmatic bounds** so merchants never sell at a loss.

---

## ??? Dual-Portal Architecture

MerchantAI cleanly separates the shopping experience from the merchant governance layer:

```
                  +---------------------------------+
                  ¦    MerchantAI Role Gateway      ¦
                  +---------------------------------+
                          ¦                 ¦
             +------------?-------+   +-----?------------------+
             ¦  ??? Buyer Portal   ¦   ¦  ?? Merchant Console   ¦
             ¦   (Customer View)  ¦   ¦   (Store Owner View)   ¦
             +--------------------+   +------------------------+
                          ¦                 ¦
             • TechBazaar Storefront        • AI Revenue & Recovery Metrics
             • AI Shopping Copilot          • Margin Bound Configuration
             • Cart & Upsell Engine         • Autonomous Agent Arena (x402)
             • In-App Razorpay Checkout     • Compliance Audit Trail (DB)
```

---

## ??? The Four Architectural Pillars ("The Bar")

1. **Bounded:**
   - LLMs can hallucinate; financial transactions cannot.
   - All financial boundaries (`MAX_DISCOUNT_PERCENT = 15%`, `MIN_MARGIN = 8%`, `MAX_ORDER_AMOUNT = 50,000`) are evaluated strictly in **deterministic Python code (`bounds.py`)**, completely decoupled from the LLM prompt.

2. **Gated:**
   - An AI cannot charge a customer without explicit human-in-the-loop authorization.
   - The conversational agent prepares the order and calculates the discount, but transfers execution to a dedicated **Payment Gate Modal**, requiring the customer to review the itemized breakdown and confirm payment via the official **Razorpay Checkout SDK**.

3. **Audited:**
   - Every agent reasoning step, catalog query, discount calculation, boundary check, and Razorpay HMAC signature verification is immutably recorded in an SQLite **Audit Trail**.
   - Available in real-time on the **Merchant Console** for compliance verification.

4. **Graceful Failure Handling:**
   - If an item is out of stock, budget limits are exceeded, or Gemini API rate limits (HTTP 429) occur, the agent falls back to friendly conversational recovery without crashing the cart session.

---

## ??? Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy (aiosqlite), Uvicorn, Google GenAI SDK (`gemini-flash-lite-latest`), Razorpay Python SDK.
- **Frontend:** React 19, Vite, TailwindCSS v4, Framer Motion, Razorpay Standard Checkout.js.
- **Protocol:** Simulated x402 / NPCI UAP Commerce Wire for agent-to-agent autonomous negotiation.

---

## ?? Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Active Google Gemini API Key
- Razorpay Test Key ID & Secret

### 1. Clone & Configure
```bash
git clone https://github.com/YOUR_USERNAME/merchantai.git
cd merchantai
```

Create `.env` in `backend/.env` (or root):
```env
RAZORPAY_KEY_ID=rzp_test_xxxxxx
RAZORPAY_KEY_SECRET=xxxxxx
GEMINI_API_KEY=xxxxxx
```

### 2. Run Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## ?? 1-Click Deployment (Render)

This repository includes a native `render.yaml` and `build.sh` blueprint for all-in-one unified hosting:

1. Push your code to GitHub.
2. Go to [Render.com](https://render.com/) -> **New** -> **Blueprint**.
3. Connect your GitHub repository.
4. Add your Environment Variables:
   - `GEMINI_API_KEY`
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`
5. Click **Deploy**. Render will automatically build the React frontend, package it with FastAPI, and deploy it to a single live URL!

---

## ?? "What Broke at 2 AM" (Hackathon War Story)

> *"During integration testing, we migrated our database models to support dynamic cart-level discounts. While SQLAlchemy updated the Python schema, the underlying SQLite database file did not alter existing tables automatically. This caused a silent `sqlite3.OperationalError: no such column: carts.discount_percent` during live cart creation, triggering our agent fallback handler!
>
> We quickly implemented an automated migration script on startup to run `ALTER TABLE carts ADD COLUMN discount_percent FLOAT DEFAULT 0.0;` if absent, ensuring seamless backward compatibility without data loss."*

