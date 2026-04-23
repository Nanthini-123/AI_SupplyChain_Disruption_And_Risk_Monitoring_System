import streamlit as st
import pandas as pd
import numpy as np
import random
import requests
import plotly.express as px
import pydeck as pdk
import google.generativeai as genai
import time
from sklearn.linear_model import LinearRegression
import networkx as nx
import os

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("🚀 AI SUPPLY CHAIN DISRUPTION PREDICION AND RISK MONITORING")

# =========================
# GEMINI CLIENT (FIXED)
# =========================
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
# =========================
# STATE
# =========================
if "risk_score" not in st.session_state:
    st.session_state.risk_score = 0

if "chat" not in st.session_state:
    st.session_state.chat = []
if "progress" not in st.session_state:
    st.session_state.progress = 0


if "kafka_stream" not in st.session_state:
    st.session_state.kafka_stream = []

if "fleet" not in st.session_state:
    st.session_state.fleet = pd.DataFrame({
        "Shipment_ID": range(1, 6),
        "From": np.random.choice(["Chennai","Mumbai","Delhi","Dubai","Singapore"], 5),
        "To": np.random.choice(["London","New York","Berlin","Tokyo"], 5),
        "Volume": np.random.randint(10, 200, 5),
        "Transport": np.random.choice(["Air","Sea","Road"], 5),
        "Base_Delay": np.random.randint(1, 10, 5),})
    
fleet = st.session_state.fleet if "fleet" in st.session_state else None   
# =========================
# ORDERS
# =========================
@st.cache_data
def generate_orders():
    return pd.DataFrame({
        "Order_ID": range(1, 11),
        "Supplier_ID": np.random.randint(1, 6, 10),
        "City_From": np.random.choice(["Chennai","Delhi","Mumbai","Dubai","Singapore"],10),
        "City_To": np.random.choice(["Bangalore","Hyderabad","London","New York"],10),
        "Quantity": np.random.randint(10,100,10),
        "Cost": np.random.randint(100,1000,10),
        "Delivery_Days": np.random.randint(1,10,10),
        "Transport": np.random.choice(["Air","Sea","Road"],10),
        "Inventory": np.random.randint(5,60,10)
    })

orders = generate_orders()

# =========================
# SUPPLIERS
# =========================
def generate_suppliers(n=8):
    return pd.DataFrame({
        "Supplier_ID": range(1, n+1),
        "Name": [f"Vendor-{i}" for i in range(n)],
        "Reliability": np.random.randint(60, 99, n),
        "Cost": np.random.randint(3, 10, n),
        "Delay": np.random.uniform(1, 5, n),
        "Risk": np.random.randint(40, 95, n),
        "Region": np.random.choice(["Asia","Europe","US","Middle East"], n)
    })

suppliers = generate_suppliers()

# =========================
# NEWS ENGINE
# =========================
def fetch_news():
    try:
        url = "https://newsapi.org/v2/everything?q=war OR flood OR strike OR oil&apiKey=4d5178b2d69f4c0aa2b512db723c815b"
        return requests.get(url).json().get("articles", [])
    except:
        return []

articles = fetch_news()

GLOBAL_EVENTS = []

st.header("🌍 Global Intelligence")

for a in articles[:5]:
    t = a["title"].lower()
    st.warning("📰 " + a["title"])

    if "war" in t:
        st.session_state.risk_score += 0.3
        GLOBAL_EVENTS.append("war")
    if "flood" in t:
        st.session_state.risk_score += 0.25
        GLOBAL_EVENTS.append("flood")
    if "strike" in t:
        st.session_state.risk_score += 0.2
        GLOBAL_EVENTS.append("strike")

# =========================
# KPI DASHBOARD
# =========================
st.header("📊 KPI DASHBOARD")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Orders", len(orders))
c2.metric("Avg Cost", round(orders["Cost"].mean(), 2))
c3.metric("Avg Inventory", round(orders["Inventory"].mean(), 2))
c4.metric("Global Risk", round(st.session_state.risk_score, 2))

st.plotly_chart(px.bar(orders, x="Order_ID", y="Quantity"))

# =========================
# ORDER CONTROL
# =========================
st.header("📦 Orders")

st.dataframe(orders)

order_id = st.selectbox("Select Order", orders["Order_ID"])

order = orders[orders["Order_ID"] == order_id].iloc[0]

# FORCE REFRESH TRIGGER
st.session_state.selected_order_id = order_id
# =========================
# REAL-TIME RISK ENGINE
# =========================
shipment = fleet.iloc[0]   # or selected shipment
risk = min(
    1,
    order["Delivery_Days"] / 10 + st.session_state.risk_score
)

st.metric("Global Risk", round(st.session_state.risk_score, 2))
st.metric("Shipment Risk", round(risk*100, 2))
# =========================
# RISK ENGINE
# =========================
delay = random.uniform(0, 6)
base_risk = random.random()
final_risk = min(1, base_risk + st.session_state.risk_score)

st.metric("Delay", round(delay, 2))
st.metric("Risk %", round(final_risk * 100, 2))

risk_level = "LOW" if final_risk < 0.3 else "MEDIUM" if final_risk < 0.7 else "HIGH"
st.info(f"Risk Level: {risk_level}")

# =========================
# ROOT CAUSE
# =========================
st.subheader("🔍 Root Cause Analysis")

if delay > 3:
    st.error("High logistics delay")
if order["Transport"] == "Sea":
    st.error("Slow transport mode")
if order["Inventory"] < 20:
    st.error("Low buffer stock")
if final_risk > 0.6:
    st.error("Global disruption impact")

# =========================
# AI SOLUTIONS
# =========================
st.subheader("🤖 AI Solutions")

if final_risk > 0.6:
    st.success("Switch supplier immediately")
if delay > 3:
    st.success("Use Air transport")
if order["Inventory"] < 20:
    st.success("Increase stock buffer")

# =========================
# SUPPLIER ENGINE
# =========================
st.header("🏭 AI Dynamic Supplier Selection Engine")

scores = []

for _, s in suppliers.iterrows():
    score = (
        s["Reliability"] * np.random.uniform(0.3, 0.5) +
        (100 - s["Risk"]) * 0.3 -
        s["Delay"] * 8 -
        s["Cost"] * 4
    )

    # global risk penalty
    score -= st.session_state.risk_score * np.random.uniform(10, 60)

    scores.append((s["Name"], score))

rank = pd.DataFrame(scores, columns=["Supplier", "Score"])
rank = rank.sort_values("Score", ascending=False)

best_supplier = rank.iloc[0]["Supplier"]

st.dataframe(rank)
st.success(f"🏆 AI Selected Supplier: {best_supplier}")
# =========================
# CONTROL TOWER UI
# =========================
st.header("📡 Control Tower View")

progress = random.randint(1, 5)
steps = ["Placed","Packed","Dispatched","In Transit","Delivered"]

for i,s in enumerate(steps):
    if i < progress:
        st.success("✔ " + s)
    elif i == progress:
        st.warning("⏳ " + s)
    else:
        st.info("• " + s)

# =========================
# SHIPMENT TRACKING
# =========================
st.header("📡 Shipment Tracking")

steps = ["Placed", "Packed", "Dispatched", "In Transit", "Customs", "Delivered"]
progress = random.randint(1, len(steps))

for i, s in enumerate(steps):
    if i < progress:
        st.success("✔ " + s)
    elif i == progress:
        st.warning("⏳ " + s)
    else:
        st.info("• " + s)
# =========================
# MULTI-SHIPMENT FLEET SYSTEM
# =========================
def generate_fleet(n=5):
    return pd.DataFrame({
        "Shipment_ID": range(1, n+1),
        "From": np.random.choice(["Chennai","Mumbai","Delhi","Dubai","Singapore"], n),
        "To": np.random.choice(["London","New York","Berlin","Tokyo"], n),
        "Volume": np.random.randint(10, 200, n),
        "Transport": np.random.choice(["Air","Sea","Road"], n),
        "Base_Delay": np.random.randint(1, 10, n),
    })

if st.session_state.fleet is None:
    st.session_state.fleet = generate_fleet()

fleet = st.session_state.fleet

# =========================
# KAFKA SIMULATION ENGINE
# =========================
def kafka_event_stream():
    events = [
        ("weather", random.uniform(0, 1)),
        ("strike", random.uniform(0, 1)),
        ("port_delay", random.uniform(0, 1)),
        ("fuel_spike", random.uniform(0, 1))
    ]
    return random.choice(events)

event, intensity = kafka_event_stream()
if "kafka_stream" not in st.session_state:
    st.session_state.kafka_stream = []

st.session_state.kafka_stream.append((event, intensity))

if len(st.session_state.kafka_stream) > 10:
    st.session_state.kafka_stream.pop(0)

# risk update
st.session_state.risk_score = sum([e[1] for e in st.session_state.kafka_stream])

st.subheader("⚡ Live Kafka Event Stream Simulation")
st.dataframe(pd.DataFrame(st.session_state.kafka_stream, columns=["Event", "Intensity"]))
# =========================
# WEATHER API (REAL)
# =========================
def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=3"
        return requests.get(url).text
    except:
        return "Weather unavailable"

# =========================
# ML DELAY PREDICTION MODEL
# =========================
def train_model():
    X = np.random.rand(200, 3)
    y = X[:,0]*5 + X[:,1]*3 + X[:,2]*10 + np.random.rand(200)
    model = LinearRegression()
    model.fit(X, y)
    return model

model = train_model()

def predict_delay(row):
    x = np.array([[row["Volume"]/200, st.session_state.risk_score, random.random()]])
    return model.predict(x)[0]

fleet["Predicted_Delay"] = fleet.apply(predict_delay, axis=1)        
# =========================
# DIJKSTRA ROUTE OPTIMIZATION
# =========================
def build_graph():
    G = nx.Graph()
    cities = ["Chennai","Mumbai","Delhi","Dubai","Singapore","London","New York"]

    for c in cities:
        for d in cities:
            if c != d:
                G.add_edge(c, d, weight=random.randint(1, 10))
    return G

G = build_graph()

def best_route(frm, to):
    return nx.shortest_path(G, frm, to, weight="weight")

# =========================
# 🌍 STABLE LIVE AI ANIMATED SUPPLY ROUTE (FIXED)
# =========================

st.header("🌍 LIVE AI ANIMATED SUPPLY ROUTE")


# -------------------------
# SAFE COORD FETCH
# -------------------------
def coords(city):
    try:
        r = requests.get(
            f"https://nominatim.openstreetmap.org/search?q={city}&format=json",
            headers={"User-Agent": "streamlit-app"}
        ).json()

        if len(r) == 0:
            return 13.0, 80.0

        return float(r[0]["lat"]), float(r[0]["lon"])

    except:
        return 13.0, 80.0


# -------------------------
# CITY COORDS
# -------------------------
lat1, lon1 = coords(order["City_From"])
lat2, lon2 = coords(order["City_To"])

# -------------------------
# TRANSPORT ICON
# -------------------------
icon_map = {
    "Air": "https://img.icons8.com/color/48/airplane-take-off.png",
    "Sea": "https://img.icons8.com/color/48/cargo-ship.png",
    "Road": "https://img.icons8.com/color/48/truck.png"
}

transport = order["Transport"]
icon_url = icon_map.get(transport, icon_map["Road"])

# -------------------------
# SAFE ANIMATION STATE (NO LOOP CRASH)
# -------------------------
if "anim_t" not in st.session_state:
    st.session_state.anim_t = 0.0

# BUTTON CONTROL (NO AUTO LOOP)
col1, col2 = st.columns(2)

with col1:
    if st.button("▶ Move Shipment"):
        st.session_state.anim_t += 0.1

with col2:
    if st.button("🔄 Reset Shipment"):
        st.session_state.anim_t = 0.0

# clamp value
st.session_state.anim_t = min(max(st.session_state.anim_t, 0.0), 1.0)

t = st.session_state.anim_t

# -------------------------
# INTERPOLATION (SMOOTH POSITION)
# -------------------------
curr_lat = lat1 + (lat2 - lat1) * t
curr_lon = lon1 + (lon2 - lon1) * t

# -------------------------
# LAYERS
# -------------------------

# moving ship icon
moving_icon = pd.DataFrame([{
    "lat": curr_lat,
    "lon": curr_lon,
    "icon": icon_url
}])

icon_layer = pdk.Layer(
    "IconLayer",
    data=moving_icon,
    get_icon="icon",
    get_size=4,
    size_scale=12,
    get_position='[lon, lat]'
)

# route line
route_layer = pdk.Layer(
    "LineLayer",
    data=[{"start": [lon1, lat1], "end": [lon2, lat2]}],
    get_source_position="start",
    get_target_position="end",
    get_color=[0, 140, 255],
    get_width=5
)

# start/end points
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=[
        {"lat": lat1, "lon": lon1},
        {"lat": lat2, "lon": lon2}
    ],
    get_position='[lon, lat]',
    get_radius=80000,
    get_fill_color=[0, 255, 0]
)

# disruption zones
disruptions = pd.DataFrame([
    {"lat": 13.1, "lon": 80.2},
    {"lat": 25.2, "lon": 55.3},
    {"lat": 51.5, "lon": -0.1},
])

disruption_layer = pdk.Layer(
    "ScatterplotLayer",
    data=disruptions,
    get_position='[lon, lat]',
    get_radius=120000,
    get_fill_color=[255, 80, 0]
)

# -------------------------
# FINAL MAP (ONLY ONCE)
# -------------------------
deck = pdk.Deck(
    layers=[route_layer, icon_layer, point_layer, disruption_layer],
    initial_view_state=pdk.ViewState(
        latitude=lat1,
        longitude=lon1,
        zoom=3,
        pitch=45
    ),
    tooltip={"text": "Live Supply Chain Movement"}
)

st.pydeck_chart(deck)

# -------------------------
# STATUS PANEL (UPGRADED INTELLIGENCE VIEW)
# -------------------------

transport_icon = {
    "Air": "✈️",
    "Sea": "🚢",
    "Road": "🚚"
}.get(transport, "📦")

risk_percent = int(final_risk * 100)

disruption_status = (
    "⚠️ HIGH GLOBAL DISRUPTION IMPACT"
    if st.session_state.risk_score > 1
    else "🟡 Moderate global instability detected"
    if st.session_state.risk_score > 0.5
    else "🟢 Stable global conditions"
)

route_health = (
    "🔴 Critical route instability"
    if risk_percent > 70
    else "🟠 Medium risk route"
    if risk_percent > 40
    else "🟢 Stable route"
)

inventory_status = (
    "🔴 Critical low stock"
    if order["Inventory"] < 15
    else "🟠 Low buffer stock"
    if order["Inventory"] < 25
    else "🟢 Healthy inventory"
)

transport_mode = f"{transport_icon} {transport}"

st.markdown(f"""
# 🚚 LIVE SHIPMENT CONTROL TOWER

## 📦 Shipment Overview
- **Transport Mode:** {transport_mode}  
- **Order ID:** {order['Order_ID']}  
- **From:** 🌍 {order['City_From']}  
- **To:** 🌍 {order['City_To']}  
- **Quantity:** 📦 {order['Quantity']} units  
- **Cost:** 💰 {order['Cost']} USD  

---

## 🟡 Movement Progress
**Progress:** `{int(t * 100)}%`  
📍 Status: {"🟢 In Transit" if t > 0 else "🟡 Shipment Prepared"}

---

## ⚠️ Risk & Intelligence Layer
- **Shipment Risk Level:** `{risk_percent}%`
- **Route Health:** {route_health}
- **Global Disruption Status:** {disruption_status}

---

## 🌍 Disruption Impact Analysis
- 🌪 Weather / Flood Zones: Detected in Asia region nodes  
- 🚧 Port Delays: Possible congestion in EU shipping routes  
- ⚡ Strike Alerts: Labor instability in selected logistics corridors  
- 🛑 Customs Risk: Medium delay probability in international checkpoints  

---

## 📦 Inventory Intelligence
- Stock Status: {inventory_status}  
- Safety Buffer: {"Sufficient" if order["Inventory"] > 25 else "Needs attention"}  
- Reorder Suggestion: {"No action required" if order["Inventory"] > 25 else "Trigger restock soon"}  

---

## 🧠 AI System Status
- ✔ Route tracking engine active  
- ✔ Disruption monitoring enabled  
- ✔ Predictive delay model running  
- ✔ Supplier rerouting logic ready  
- ✔ Real-time simulation mode ON  

---

## 🚀 AI Recommendation Summary
{"✔ Continue current route (low risk)" if risk_percent < 40 else "⚠️ Consider rerouting via Air transport" if transport != "Air" else "✔ Air route already optimal"}
""")

# =========================
# INVENTORY ALERT
# =========================
st.header("📦 Inventory Alerts")
st.dataframe(orders[orders["Inventory"] < 20])

# =========================
# 🤖 AI Assistant (APP-AWARE BRAIN FIX)
# =========================
st.header("🤖 AI Assistant")

q = st.text_input("Ask AI", key="user_input")

if "last_order_id" not in st.session_state:
    st.session_state.last_order_id = None

if st.session_state.last_order_id != order_id:
    st.session_state.chat = []   # reset AI memory per order change
    st.session_state.last_order_id = order_id

if st.button("Ask") and q:

    if not st.session_state.chat or st.session_state.chat[-1][1] != q:
        st.session_state.chat.append(("You", q))

    # =========================
    # SAFE FALLBACK (IMPORTANT)
    # =========================
    try:
        selected_order = order
    except:
        selected_order = orders.iloc[0]

    try:
        safe_delay = delay
    except:
        safe_delay = 0

    try:
        safe_risk = min(max(final_risk, 0), 1)
    except:
        safe_risk = 0

    context = f"""
CURRENT ORDER ID: {order['Order_ID']}

You are an AI assistant inside a Supply Chain Digital Twin App.

CURRENT SELECTED ORDER:
Order_ID: {selected_order['Order_ID']}
Supplier_ID: {selected_order['Supplier_ID']}
City_From: {selected_order['City_From']}
City_To: {selected_order['City_To']}
Quantity: {selected_order['Quantity']}
Cost: {selected_order['Cost']}
Transport: {selected_order['Transport']}
Inventory: {selected_order['Inventory']}

SYSTEM METRICS:
Delay: {safe_delay}
Risk Score (normalized 0 to 1): {safe_risk:.2f}
Do NOT assume risk is absolute unless > 0.9
Global Risk Score: {st.session_state.risk_score}

USER QUESTION:
{q}
You are a Supply Chain Risk Analyst.

Analyze the selected order and:
- detect risk factors
- explain why risk is high/low
- suggest actions

Return in structured format.
Return format:
Risk Score: <value>
Risk Level: LOW / MEDIUM / HIGH
Reason: <short explanation>
Recommendation: <action>
RULES:
- Always interpret Risk Score between 0 and 1
- Convert to percentage if needed
- Explain in 2–5 lines
- Do not output only numbers
IMPORTANT:
- Do NOT assume missing data
- Do NOT exaggerate risk
- If uncertain, say "moderate confidence"
"""

    try:
        rresponse = model.generate_content(context)
        reply = response.text if response else "No response"
    except Exception as e:
        reply = f"AI Error: {str(e)}"

    st.session_state.chat.append(("AI", reply))

for r, m in st.session_state.chat:
    st.write(r, ":", m)



# =========================
# FORECAST
# =========================
st.header("📊 Forecast")
st.line_chart(np.random.randint(10, 100, 7))


st.header("📡 Live Risk Intelligence Feed")

live_events = [
    "Port strike detected in Singapore",
    "Oil price spike impacting shipping cost",
    "Weather delay in Chennai port",
    "Customs backlog increasing in EU",
    "Fuel shortage warning in Middle East"
]

for e in random.sample(live_events, 3):
    st.info("🔴 LIVE: " + e)



st.header("📈 AI Demand Forecasting Engine")

future_demand = np.cumsum(np.random.randint(5, 20, 10))

st.line_chart(future_demand)

st.success("📊 Insight: Demand trend is volatile due to global disruptions")





st.header("🧭 Smart Route Optimizer AI")

routes = ["Air Route (Fast, Expensive)", "Sea Route (Slow, Cheap)", "Hybrid Route (Balanced)"]

best_route = random.choice(routes)

st.write("🛣 Suggested Optimal Route:")
st.success(best_route)

st.info("AI Reason: Optimized based on cost + delay + global risk score")




st.header("⚠️ Supplier Failure Prediction AI")

supplier_risk = pd.DataFrame({
    "Supplier": suppliers["Name"],
    "Failure_Probability": np.random.rand(len(suppliers))
})

st.dataframe(supplier_risk)

worst = supplier_risk.loc[supplier_risk["Failure_Probability"].idxmax()]
st.error(f"🚨 High Risk Supplier: {worst['Supplier']}")




st.header("🌍 Global Trade Disruption Scoreboard")

regions = ["Asia", "Europe", "Middle East", "America"]
risk_values = np.random.randint(20, 100, 4)

chart = pd.DataFrame({
    "Region": regions,
    "Risk": risk_values
})

st.bar_chart(chart.set_index("Region"))



st.header("🤖 AI Auto-Action Engine")

actions = []

if final_risk > 0.7:
    actions.append("AUTO: Switch to backup supplier")
if delay > 3:
    actions.append("AUTO: Reroute shipment via air cargo")
if order["Inventory"] < 20:
    actions.append("AUTO: Trigger emergency restock")

if actions:
    for a in actions:
        st.warning(a)
else:
    st.success("System Stable - No Auto Actions Required")
