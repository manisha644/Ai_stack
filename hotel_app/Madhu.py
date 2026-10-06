import streamlit as st
import ollama
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Madhavi Tiffin Center",
    page_icon="🥘",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #fffaf2;
}

.title {
    text-align: center;
    font-size: 45px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    font-size: 20px;
}

.card {
    padding: 20px;
    border-radius: 18px;
    background-color: #fff3df;
    border: 1px solid #f0d5aa;
    margin-bottom: 15px;
}

.price {
    font-size: 22px;
    font-weight: bold;
}

.big-button {
    text-align: center;
    font-size: 20px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FOOD DATA
# --------------------------------------------------

tiffins = {
    "🥞 Plain Dosa": {"price": 40, "rating": 4.5, "desc": "Crispy dosa served with chutney and sambar."},
    "🥔 Masala Dosa": {"price": 60, "rating": 4.8, "desc": "Crispy dosa filled with delicious potato masala."},
    "🍚 Idli": {"price": 30, "rating": 4.7, "desc": "Soft and fluffy idlis with chutney and sambar."},
    "🍛 Vada": {"price": 35, "rating": 4.6, "desc": "Crispy golden vada served hot."},
    "🥣 Puri": {"price": 45, "rating": 4.5, "desc": "Soft and tasty puri served with curry."},
    "🌯 Mysore Bonda": {"price": 40, "rating": 4.6, "desc": "Soft and crispy South Indian snack."},
    "🍲 Upma": {"price": 35, "rating": 4.3, "desc": "Fresh and healthy traditional upma."},
    "🌶️ Pongal": {"price": 45, "rating": 4.7, "desc": "Hot and tasty South Indian pongal."}
}

drinks = {
    "☕ Tea": {"price": 15, "rating": 4.5, "desc": "Fresh hot tea."},
    "☕ Coffee": {"price": 20, "rating": 4.8, "desc": "Fresh filter coffee."},
    "🥛 Milk": {"price": 20, "rating": 4.3, "desc": "Fresh milk."},
    "🥤 Fresh Juice": {"price": 40, "rating": 4.5, "desc": "Refreshing fresh fruit juice."},
    "🥛 Badam Milk": {"price": 40, "rating": 4.7, "desc": "Healthy and delicious badam milk."}
}

snacks = {
    "🍔 Veg Sandwich": {"price": 50, "rating": 4.4, "desc": "Fresh vegetable sandwich."},
    "🥪 Bread Bajji": {"price": 30, "rating": 4.5, "desc": "Crispy bread bajji."},
    "🍟 French Fries": {"price": 50, "rating": 4.4, "desc": "Crispy golden fries."},
    "🌶️ Mirchi Bajji": {"price": 30, "rating": 4.6, "desc": "Spicy and crispy mirchi bajji."},
    "🥟 Samosa": {"price": 20, "rating": 4.5, "desc": "Crispy samosa with tasty filling."},
    "🍘 Punugulu": {"price": 40, "rating": 4.7, "desc": "Crispy South Indian punugulu."}
}

all_food = {}
all_food.update(tiffins)
all_food.update(drinks)
all_food.update(snacks)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "cart" not in st.session_state:
    st.session_state.cart = {}

if "orders" not in st.session_state:
    st.session_state.orders = []

if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {
            "name": "Priya",
            "rating": 5,
            "review": "Very tasty food and good service! ❤️"
        },
        {
            "name": "Rahul",
            "rating": 5,
            "review": "Feels just like homemade food! 😋"
        }
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_order" not in st.session_state:
    st.session_state.last_order = None

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

def add_to_cart(item):
    if item in st.session_state.cart:
        st.session_state.cart[item] += 1
    else:
        st.session_state.cart[item] = 1
    st.success(f"{item} added to cart! 🛒")


def cart_total():
    total = 0

    for item, quantity in st.session_state.cart.items():
        total += all_food[item]["price"] * quantity

    return total


def change_quantity(item, amount):

    if item in st.session_state.cart:
        st.session_state.cart[item] += amount

        if st.session_state.cart[item] <= 0:
            del st.session_state.cart[item]


def remove_item(item):

    if item in st.session_state.cart:
        del st.session_state.cart[item]


def show_food_items(food_data):

    for item, details in food_data.items():

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"### {item}")
            st.write(details["desc"])

        with col2:
            st.write(f"⭐ {details['rating']}")
            st.markdown(f"### ₹{details['price']}")

        with col3:
            if st.button("➕ Add", key="add_" + item):
                add_to_cart(item)


def create_bill(order):

    bill = f"""
🥘 MADHAVI TIFFIN CENTER
━━━━━━━━━━━━━━━━━━━━━━

🧾 Order ID: {order['id']}

👤 Customer: {order['name']}
📞 Phone: {order['phone']}

🍽️ ITEMS
"""

    for item, quantity in order["items"].items():
        price = all_food[item]["price"] * quantity
        bill += f"{item} x {quantity} = ₹{price}\n"

    bill += f"""
━━━━━━━━━━━━━━━━━━━━━━

💰 Subtotal: ₹{order['subtotal']}
🚚 Delivery: ₹{order['delivery']}
💵 TOTAL: ₹{order['total']}

💳 Payment: {order['payment']}

📍 Address:
{order['address']}

⏰ Preparation Time: 20-30 minutes

❤️ Thank you for ordering from
Madhavi Tiffin Center!

Fresh Taste • Homely Food • Happy Moments ❤️
"""

    return bill

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🥘 MADHAVI")
st.sidebar.subheader("Tiffin Center ❤️")

pages = [
    "🏠 Home",
    "🍽️ Menu",
    "🥞 Tiffins",
    "☕ Drinks",
    "🍟 Snacks",
    "🛒 Cart",
    "📦 Order",
    "🎁 Offers",
    "⭐ Reviews",
    "🤖 AI Assistant",
    "📊 Owner Dashboard",
    "ℹ️ About Us",
    "📞 Contact"
]

st.session_state.page = st.sidebar.radio(
    "📍 Navigate",
    pages
)

st.sidebar.markdown("---")
st.sidebar.info("🥘 Fresh • Tasty • Homemade")

# ==================================================
# HOME
# ==================================================

if st.session_state.page == "🏠 Home":

    st.markdown(
        '<div class="title">🥘 MADHAVI TIFFIN CENTER ☕</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Fresh Taste • Homely Food • Happy Moments ❤️</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.success(
        "❤️ Welcome to Madhavi Tiffin Center! "
        "Enjoy delicious South Indian food with a homely taste."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 🍽️")
        st.write("Fresh & Tasty")

    with col2:
        st.markdown("### ❤️")
        st.write("Homemade Taste")

    with col3:
        st.markdown("### ☕")
        st.write("Freshly Prepared")

    with col4:
        st.markdown("### 😊")
        st.write("Affordable Prices")

    st.markdown("---")

    st.header("🌟 TODAY'S SPECIAL")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ## 🥞 Masala Dosa + ☕ Tea

        ⭐ 4.9 Rating

        Crispy Masala Dosa with hot fresh tea.

        ### 💰 Combo Price: ₹70
        """)

        if st.button("🔥 Order Special"):
            add_to_cart("🥔 Masala Dosa")
            add_to_cart("☕ Tea")

    with col2:
        st.markdown("""
        ## ❤️ Why Choose Us?

        🍚 Fresh Ingredients  
        👩‍🍳 Homemade Taste  
        💰 Affordable Prices  
        😊 Friendly Service  
        ✨ Freshly Prepared Food
        """)

    st.markdown("---")

    st.header("🚀 Quick Actions")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("🍽️ View Menu"):
            st.session_state.page = "🍽️ Menu"
            st.rerun()

    with c2:
        if st.button("🛒 Order Now"):
            st.session_state.page = "🛒 Cart"
            st.rerun()

    with c3:
        if st.button("🤖 Ask AI"):
            st.session_state.page = "🤖 AI Assistant"
            st.rerun()

    with c4:
        if st.button("📞 Contact Us"):
            st.session_state.page = "📞 Contact"
            st.rerun()

# ==================================================
# MENU
# ==================================================

elif st.session_state.page == "🍽️ Menu":

    st.title("🍽️ Madhavi Food Menu")
    st.write("Choose your favourite food 😋")

    tab1, tab2, tab3 = st.tabs(
        ["🥞 Tiffins", "☕ Drinks", "🍟 Snacks"]
    )

    with tab1:
        show_food_items(tiffins)

    with tab2:
        show_food_items(drinks)

    with tab3:
        show_food_items(snacks)

# ==================================================
# TIFFINS
# ==================================================

elif st.session_state.page == "🥞 Tiffins":

    st.title("🥞 South Indian Tiffins")
    show_food_items(tiffins)

# ==================================================
# DRINKS
# ==================================================

elif st.session_state.page == "☕ Drinks":

    st.title("☕ Fresh Drinks")
    show_food_items(drinks)

# ==================================================
# SNACKS
# ==================================================

elif st.session_state.page == "🍟 Snacks":

    st.title("🍟 Evening Snacks")
    show_food_items(snacks)

# ==================================================
# CART
# ==================================================

elif st.session_state.page == "🛒 Cart":

    st.title("🛒 YOUR CART")

    if len(st.session_state.cart) == 0:

        st.info("🛒 Your cart is empty.")

        if st.button("🍽️ Go to Menu"):
            st.session_state.page = "🍽️ Menu"
            st.rerun()

    else:

        for item, quantity in list(st.session_state.cart.items()):

            col1, col2, col3, col4, col5 = st.columns(
                [3, 1, 1, 1, 1]
            )

            with col1:
                st.write(f"### {item}")

            with col2:
                st.write(f"₹{all_food[item]['price']}")

            with col3:
                if st.button("➖", key="minus_" + item):
                    change_quantity(item, -1)
                    st.rerun()

            with col4:
                st.write(quantity)

                if st.button("➕", key="plus_" + item):
                    change_quantity(item, 1)
                    st.rerun()

            with col5:
                if st.button("❌", key="remove_" + item):
                    remove_item(item)
                    st.rerun()

        st.markdown("---")

        subtotal = cart_total()
        delivery = 20
        total = subtotal + delivery

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧾 Price Details")
            st.write(f"💰 Subtotal: ₹{subtotal}")
            st.write(f"🚚 Delivery: ₹{delivery}")
            st.write(f"### 💵 Grand Total: ₹{total}")

        with col2:

            if st.button("✅ Place Order", use_container_width=True):
                st.session_state.page = "📦 Order"
                st.rerun()

            if st.button("🗑️ Clear Cart", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()

# ==================================================
# ORDER
# ==================================================

elif st.session_state.page == "📦 Order":

    st.title("📦 Place Your Order")

    if len(st.session_state.cart) == 0:

        st.warning("🛒 Please add items to your cart first.")

    else:

        subtotal = cart_total()
        delivery = 20
        total = subtotal + delivery

        st.write("### 🍽️ Your Items")

        for item, quantity in st.session_state.cart.items():
            st.write(
                f"{item} × {quantity} = "
                f"₹{all_food[item]['price'] * quantity}"
            )

        st.markdown("---")

        with st.form("order_form"):

            name = st.text_input("👤 Customer Name")
            phone = st.text_input("📞 Phone Number")
            address = st.text_area("🏠 Delivery Address")

            payment = st.radio(
                "💳 Payment Method",
                [
                    "💵 Cash on Delivery",
                    "📱 UPI",
                    "💳 Card"
                ]
            )

            confirm = st.form_submit_button(
                "✅ Confirm Order"
            )

            if confirm:

                if name == "":
                    st.error("⚠️ Please enter your name.")

                elif phone == "":
                    st.error("⚠️ Please enter your phone number.")

                elif address == "":
                    st.error("⚠️ Please enter your address.")

                else:

                    order_id = "MT" + str(
                        1000 + len(st.session_state.orders) + 1
                    )

                    order = {
                        "id": order_id,
                        "name": name,
                        "phone": phone,
                        "address": address,
                        "payment": payment,
                        "items": dict(st.session_state.cart),
                        "subtotal": subtotal,
                        "delivery": delivery,
                        "total": total,
                        "time": datetime.now().strftime(
                            "%d-%m-%Y %H:%M"
                        )
                    }

                    st.session_state.orders.append(order)
                    st.session_state.last_order = order

                    st.session_state.cart = {}

                    st.success(
                        "🎉 ORDER CONFIRMED SUCCESSFULLY!"
                    )

                    st.balloons()

                    st.write(f"🧾 Order ID: **{order_id}**")
                    st.write(f"👤 Customer: **{name}**")
                    st.write(f"💰 Total: **₹{total}**")
                    st.write(
                        "⏰ Estimated Preparation Time: "
                        "**20-30 minutes**"
                    )

# ==================================================
# OFFERS
# ==================================================

elif st.session_state.page == "🎁 Offers":

    st.title("🎁 Special Offers")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ## 🔥 Morning Combo

        🥞 2 Idli  
        🍛 1 Vada  
        ☕ Tea

        ### 💰 ₹60
        """)

        if st.button("🎁 Grab Offer 1"):
            add_to_cart("🍚 Idli")
            add_to_cart("🍚 Idli")
            add_to_cart("🍛 Vada")
            add_to_cart("☕ Tea")

    with col2:
        st.markdown("""
        ## 🌟 Breakfast Combo

        🥞 Dosa  
        🍛 Vada  
        ☕ Coffee

        ### 💰 ₹100
        """)

        if st.button("🎁 Grab Offer 2"):
            add_to_cart("🥔 Masala Dosa")
            add_to_cart("🍛 Vada")
            add_to_cart("☕ Coffee")

    with col3:
        st.markdown("""
        ## 👨‍👩‍👧 Family Combo

        🍽️ 4 Tiffins  
        ☕ 4 Drinks

        ### 💰 ₹250
        """)

        if st.button("🎁 Grab Offer 3"):
            st.info("Family Combo added! Please select your items from Menu.")

# ==================================================
# REVIEWS
# ==================================================

elif st.session_state.page == "⭐ Reviews":

    st.title("⭐ Customer Reviews")

    with st.form("review_form"):

        name = st.text_input("👤 Your Name")

        rating = st.select_slider(
            "⭐ Rating",
            options=[1, 2, 3, 4, 5],
            value=5
        )

        review = st.text_area("💬 Your Review")

        submit = st.form_submit_button(
            "📤 Submit Review"
        )

        if submit:

            if name and review:

                st.session_state.reviews.append({
                    "name": name,
                    "rating": rating,
                    "review": review
                })

                st.success("❤️ Thank you for your review!")

            else:
                st.warning("⚠️ Please fill all fields.")

    st.markdown("---")

    for review in st.session_state.reviews:

        st.markdown(
            f"### 👤 {review['name']}"
        )

        st.write(
            "⭐" * review["rating"]
        )

        st.write(
            f"💬 {review['review']}"
        )

        st.markdown("---")

# ==================================================
# AI ASSISTANT
# ==================================================

elif st.session_state.page == "🤖 AI Assistant":

    st.title("🤖 Madhavi Food Assistant")

    st.write(
        "Ask me anything about Madhavi Tiffin Center! 🥘❤️"
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input(
        "Ask about menu, prices, timings..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.write(question)

        system_prompt = """
You are Madhavi Food Assistant.

You are the official AI assistant of Madhavi Tiffin Center.

Only use the following information.

MENU:

Plain Dosa - ₹40
Masala Dosa - ₹60
Idli - ₹30
Vada - ₹35
Puri - ₹45
Mysore Bonda - ₹40
Upma - ₹35
Pongal - ₹45

Tea - ₹15
Coffee - ₹20
Milk - ₹20
Fresh Juice - ₹40
Badam Milk - ₹40

Veg Sandwich - ₹50
Bread Bajji - ₹30
French Fries - ₹50
Mirchi Bajji - ₹30
Samosa - ₹20
Punugulu - ₹40

Opening Hours:
Morning: 6:00 AM - 11:00 AM
Evening: 5:00 PM - 10:00 PM

Delivery charge: ₹20

Preparation time: 20-30 minutes

You should answer politely and briefly.

If the user asks about something not related to Madhavi Tiffin Center,
say that you can help only with Madhavi Tiffin Center information.

Never invent food items or prices.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(st.session_state.messages)

        try:

            response = ollama.chat(
                model="llama3.2:3b",
                messages=messages
            )

            answer = response["message"]["content"]

        except Exception as e:

            answer = (
                "⚠️ Ollama is not running or the model is not installed.\n\n"
                "Please run:\n"
                "ollama pull llama3.2:3b"
            )

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

# ==================================================
# OWNER DASHBOARD
# ==================================================

elif st.session_state.page == "📊 Owner Dashboard":

    st.title("📊 Owner Dashboard")

    total_orders = len(st.session_state.orders)

    total_sales = sum(
        order["total"]
        for order in st.session_state.orders
    )

    average_rating = 0

    if st.session_state.reviews:

        average_rating = sum(
            review["rating"]
            for review in st.session_state.reviews
        ) / len(st.session_state.reviews)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📦 Total Orders",
            total_orders
        )

    with col2:
        st.metric(
            "💰 Total Sales",
            f"₹{total_sales}"
        )

    with col3:
        st.metric(
            "⭐ Average Rating",
            round(average_rating, 1)
        )

    with col4:
        st.metric(
            "🍽️ Menu Items",
            len(all_food)
        )

    st.markdown("---")

    st.header("📦 Recent Orders")

    if total_orders == 0:

        st.info("No orders yet.")

    else:

        for order in st.session_state.orders:

            st.markdown(f"""
            ### 🧾 {order['id']}

            👤 {order['name']}  
            💰 ₹{order['total']}  
            ⏰ {order['time']}
            """)

            st.markdown("---")

# ==================================================
# ABOUT
# ==================================================

elif st.session_state.page == "ℹ️ About Us":

    st.title("❤️ About Madhavi Tiffin Center")

    st.markdown("""
    ### 🥘 Our Story

    At Madhavi Tiffin Center, we serve fresh,
    tasty and affordable South Indian food
    with a homely touch.

    ### 🌟 Why Choose Us?

    🍚 Fresh Ingredients

    👩‍🍳 Homemade Taste

    💰 Affordable Prices

    😊 Friendly Service

    ✨ Freshly Prepared Food

    ❤️ Happy Customers
    """)

# ==================================================
# CONTACT
# ==================================================

elif st.session_state.page == "📞 Contact":

    st.title("📞 Contact Madhavi Tiffin Center")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        ## 📍 Location

        🥘 Madhavi Tiffin Center

        📍 Your Local Area

        ## 📞 Phone

        📞 98765 43210

        ## 📧 Email

        📧 madhavitiffin@example.com
        """)

    with col2:

        st.markdown("""
        ## 🕐 Opening Hours

        🌅 Morning: 6:00 AM – 11:00 AM

        🌆 Evening: 5:00 PM – 10:00 PM

        ## 🚚 Delivery

        🚚 Available

        💰 Delivery Charge: ₹20
        """)

    st.markdown("---")

    st.header("💬 Send Us a Message")

    name = st.text_input("👤 Name")
    email = st.text_input("📧 Email")
    message = st.text_area("💬 Message")

    if st.button("📤 Send Message"):

        if name and email and message:
            st.success(
                "🎉 Thank you! Your message has been received."
            )
        else:
            st.warning(
                "⚠️ Please fill all fields."
            )

# ==================================================
# BILL
# ==================================================

if st.session_state.last_order is not None:

    if st.session_state.page == "📦 Order":

        st.markdown("---")

        st.header("🧾 Your Bill")

        bill = create_bill(
            st.session_state.last_order
        )

        st.code(bill)

        st.download_button(
            "🧾 Generate Bill",
            data=bill,
            file_name="madhavi_bill.txt",
            mime="text/plain"
        )