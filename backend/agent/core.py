import os
import asyncio
from google import genai
from google.genai import types
from agent.prompts import SYSTEM_PROMPT
from agent.tools import search_products, get_product_details, add_to_cart, remove_from_cart, view_cart, suggest_related, apply_discount, create_order, check_payment_status
from dataclasses import dataclass, field
from config import settings

@dataclass
class AgentResponse:
    text: str
    products: list = field(default_factory=list)
    cart_update: dict = None
    order_info: dict = None
    audit_entries: list = field(default_factory=list)

# Global in-memory storage for session histories (for demo purposes)
SESSION_HISTORIES = {}

class AgentCore:
    def __init__(self, session_id: str):
        self.session_id = session_id
        if not settings.GEMINI_API_KEY:
            self.client = None
        else:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        if self.session_id not in SESSION_HISTORIES:
            SESSION_HISTORIES[self.session_id] = []
        self.history = SESSION_HISTORIES[self.session_id]

    async def process_message(self, user_message: str) -> AgentResponse:
        if not self.client:
            return AgentResponse(text="Error: GEMINI_API_KEY is missing. Please configure it in .env to use the AI assistant.")

        # Shared state to capture UI updates from tool calls
        ui_state = {"products": [], "cart_update": None, "order_info": None}

        # --- Wrapped Tool Functions for Gemini ---
        # We wrap these so Gemini doesn't have to guess the session_id
        async def wrapped_search_products(query: str, max_price: float = None, category: str = None):
            """Search the catalog for products based on a query."""
            res = await search_products(query, max_price, category)
            if isinstance(res, list): ui_state["products"] = res
            return res

        async def wrapped_get_product_details(product_id: int):
            """Get detailed information about a specific product."""
            return await get_product_details(product_id)

        async def wrapped_add_to_cart(product_id: int = None, product_name: str = None, quantity: int = 1):
            """Add a specified product to the user's cart by its ID or name."""
            res = await add_to_cart(self.session_id, product_id=product_id, product_name=product_name, quantity=quantity)
            if "error" not in res: 
                ui_state["cart_update"] = {"items": "updated", "total": res.get("cart_total", 0)}
                if res.get("suggested_upsells"):
                    ui_state["products"] = res.get("suggested_upsells")
            return res

        async def wrapped_remove_from_cart(product_id: int):
            """Remove a product from the user's cart."""
            res = await remove_from_cart(self.session_id, product_id)
            if "error" not in res: ui_state["cart_update"] = {"items": "updated", "total": "Check cart"}
            return res

        async def wrapped_view_cart():
            """View the current contents and total of the user's cart."""
            res = await view_cart(self.session_id)
            ui_state["cart_update"] = {"items": len(res.get("items", [])), "total": res.get("total", 0)}
            return res

        async def wrapped_suggest_related(product_id: int):
            """Get related product suggestions to upsell or cross-sell."""
            res = await suggest_related(product_id)
            if isinstance(res, list): ui_state["products"] = res
            return res

        async def wrapped_apply_discount(discount_percent: float):
            """Apply a discount percentage to the cart."""
            return await apply_discount(self.session_id, discount_percent)

        async def wrapped_create_order():
            """Create a payment order for the current cart contents. MUST be explicitly confirmed by the user first."""
            res = await create_order(self.session_id)
            if "error" not in res: ui_state["order_info"] = res
            return res

        async def wrapped_check_payment_status(order_id: int):
            """Check the status of an order payment."""
            return await check_payment_status(order_id)

        tool_funcs = [
            wrapped_search_products, wrapped_get_product_details, wrapped_add_to_cart,
            wrapped_remove_from_cart, wrapped_view_cart, wrapped_suggest_related,
            wrapped_apply_discount, wrapped_create_order, wrapped_check_payment_status
        ]

        # Add user message to history
        self.history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))
        
        for _ in range(5):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model='gemini-flash-lite-latest',
                        contents=self.history,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            tools=tool_funcs,
                            temperature=0.0,
                            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                        )
                    ),
                    timeout=12.0
                )
            except asyncio.TimeoutError:
                return AgentResponse(text="⏳ AI response timed out. The Gemini API took longer than expected. Please try re-sending your message!")
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str.upper():
                    return AgentResponse(text="The AI service is temporarily unavailable. Please try again in a moment.")
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    return AgentResponse(text="⏳ Gemini API rate limit reached (5 req/min free tier). Please wait 15 seconds and try again!")
                return AgentResponse(text="The AI service is temporarily unavailable. Please try again in a moment.")

            if not response.candidates:
                return AgentResponse(text="I encountered an error generating a response.")

            model_message = response.candidates[0].content
            self.history.append(model_message)

            # Handle function calls
            if response.function_calls:
                function_responses_parts = []
                for fc in response.function_calls:
                    func = next((f for f in tool_funcs if f.__name__ == fc.name), None)
                    if func:
                        try:
                            # Execute the tool safely
                            result = await func(**fc.args)
                        except Exception as e:
                            result = {"error": str(e)}
                        
                        # Prepare the function response part
                        resp_data = result if isinstance(result, dict) else {"result": result}
                        function_responses_parts.append(
                            types.Part.from_function_response(name=fc.name, response=resp_data)
                        )
                
                # Append the function results back to the conversation as user input
                self.history.append(types.Content(role="user", parts=function_responses_parts))
                continue # Loop back to let the model see the results and respond
            
            # If no function calls, the model gave a text response
            return AgentResponse(
                text=response.text,
                products=ui_state["products"],
                cart_update=ui_state["cart_update"],
                order_info=ui_state["order_info"]
            )

        return AgentResponse(text="I'm sorry, the operation timed out. Please try again.")
