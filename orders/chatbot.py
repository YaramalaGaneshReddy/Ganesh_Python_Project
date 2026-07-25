import re
from .models import Order

# Store Policy Knowledge Documents (RAG Context Base)
STORE_POLICIES = {
    "cancellation_policy": (
        "Orders can be cancelled at any time before they are shipped (i.e. status is Pending or Paid). "
        "Once an order status reaches 'Shipped' or 'Delivered', it cannot be cancelled directly. "
        "You can request a return/refund within 14 days of delivery."
    ),
    "tracking_policy": (
        "Standard delivery takes 2 to 5 business days after dispatch. "
        "You can view real-time tracking updates directly in your Order History page."
    ),
    "refund_policy": (
        "Refunds for cancelled orders are initiated automatically and processed back to your payment method within 3 to 5 business days."
    )
}

def process_rag_query(user, message):
    """
    RAG Assistant Engine: Contextually retrieves user orders & store policy to answer tracking & cancellation queries.
    """
    msg_lower = message.lower().strip()
    
    # Extract order ID if provided in message (e.g. "cancel order 3" or "where is order #4")
    order_id_match = re.search(r'(?:order|id|#)\s*#?(\d+)', msg_lower)
    target_order_id = int(order_id_match.group(1)) if order_id_match else None
    
    # Retrieve user's orders context
    user_orders = []
    if user.is_authenticated:
        user_orders = list(Order.objects.filter(user=user).order_by('-created_at'))
    
    # Handle direct cancellation request
    if "cancel" in msg_lower:
        if target_order_id:
            try:
                order = Order.objects.get(id=target_order_id, user=user) if user.is_authenticated else Order.objects.get(id=target_order_id)
                if order.status in ['Pending', 'Paid']:
                    order.status = 'Cancelled'
                    order.save()
                    return {
                        "reply": f"✅ Success! **Order #{order.id}** has been successfully **Cancelled**. A refund request of **${order.total_price}** has been initiated.",
                        "action": "order_cancelled",
                        "order_id": order.id
                    }
                elif order.status == 'Cancelled':
                    return {
                        "reply": f"ℹ️ **Order #{order.id}** was already cancelled previously.",
                        "action": "info"
                    }
                else:
                    return {
                        "reply": f"⚠️ **Order #{order.id}** cannot be cancelled because its status is already **'{order.status}'**. {STORE_POLICIES['cancellation_policy']}",
                        "action": "info"
                    }
            except Order.DoesNotExist:
                return {
                    "reply": f"❌ We couldn't find Order #{target_order_id} associated with your account. Please check your order number.",
                    "action": "error"
                }
        else:
            # Provide general cancellation instructions & list cancellable orders
            cancellable = [o for o in user_orders if o.status in ['Pending', 'Paid']]
            if cancellable:
                orders_list = ", ".join([f"**#{o.id}** (${o.total_price} - {o.status})" for o in cancellable])
                return {
                    "reply": f"📋 {STORE_POLICIES['cancellation_policy']}\n\nYour active orders eligible for cancellation are: {orders_list}.\n\n*To cancel, reply with 'Cancel Order #[number]'.*",
                    "action": "info"
                }
            else:
                return {
                    "reply": f"📋 {STORE_POLICIES['cancellation_policy']}\n\nYou currently have no pending orders eligible for cancellation.",
                    "action": "info"
                }
                
    # Handle tracking / status query
    if any(k in msg_lower for k in ["track", "status", "where", "delivery", "history", "order"]):
        if target_order_id:
            try:
                order = Order.objects.get(id=target_order_id, user=user) if user.is_authenticated else Order.objects.get(id=target_order_id)
                items_str = ", ".join([f"{item.quantity}x {item.product.name if item.product else 'Item'}" for item in order.items.all()])
                return {
                    "reply": f"📦 **Order #{order.id} Details**:\n- **Status**: `{order.status}`\n- **Items**: {items_str}\n- **Total**: ${order.total_price}\n- **Placed On**: {order.created_at.strftime('%b %d, %Y')}\n\n{STORE_POLICIES['tracking_policy']}",
                    "action": "info"
                }
            except Order.DoesNotExist:
                return {
                    "reply": f"❌ Order #{target_order_id} was not found. Please double-check your Order ID.",
                    "action": "error"
                }
        elif user_orders:
            latest = user_orders[0]
            items_str = ", ".join([f"{item.quantity}x {item.product.name if item.product else 'Item'}" for item in latest.items.all()])
            return {
                "reply": f"🔍 Here is your latest order **#{latest.id}**:\n- **Status**: `{latest.status}`\n- **Items**: {items_str}\n- **Total**: ${latest.total_price}\n- **Placed On**: {latest.created_at.strftime('%b %d, %Y')}\n\n{STORE_POLICIES['tracking_policy']}",
                "action": "info"
            }
        else:
            return {
                "reply": f"ℹ️ You have no order history yet. Once you place an order, you can track it live right here! {STORE_POLICIES['tracking_policy']}",
                "action": "info"
            }
            
    # Default RAG Response with store capabilities summary
    return {
        "reply": (
            "🤖 **Hi! I am your AI Assistant.** I can help you with:\n"
            "1. **Track Order**: Ask 'Where is my order?' or 'Track order #12'\n"
            "2. **Cancel Order**: Ask 'Cancel order #12' or 'Can I cancel my order?'\n"
            "3. **Return Policy**: Learn about refunds & shipping times."
        ),
        "action": "info"
    }
