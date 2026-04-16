import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os  # <- added to handle folder creation

# Make sure dataset folder exists
os.makedirs('dataset', exist_ok=True)

# Number of orders to simulate
n_orders = 5000
np.random.seed(42)

# Suppliers and reliability
suppliers = ['S1','S2','S3','S4','S5']
supplier_reliability = {'S1': 90, 'S2': 80, 'S3': 85, 'S4': 70, 'S5': 60}

# Items and categories
items = ['Laptop','Phone','Shirt','Shoes','Watch']
categories = {'Laptop':'Electronics','Phone':'Electronics','Shirt':'Apparel','Shoes':'Apparel','Watch':'Accessories'}
transport_modes = ['Air','Sea','Road','Rail']

data = []

for i in range(1, n_orders+1):
    order_id = f"O{i:05d}"
    customer_id = f"C{random.randint(1,1000):04d}"
    item = random.choice(items)
    item_category = categories[item]
    order_quantity = random.randint(1,20)
    supplier = random.choice(suppliers)
    reliability = supplier_reliability[supplier]
    inventory = random.randint(0,100)
    cost_per_unit = random.randint(50,1000)
    total_cost = cost_per_unit * order_quantity
    transport = random.choice(transport_modes)
    distance = random.randint(50,5000)  # km
    order_date = (datetime.today() - timedelta(days=random.randint(1,60))).strftime("%Y-%m-%d")  # <- format date as string
    expected_days = max(1,int(distance/500)) + random.randint(1,3)
    # Simulate actual delivery based on supplier reliability and randomness
    actual_days = expected_days + (0 if np.random.rand() < reliability/100 else random.randint(1,5))
    delay = 1 if actual_days > expected_days else 0
    disruption = 1 if (delay==1 and inventory<order_quantity) else 0
    stock_risk = max(0, (order_quantity - inventory)/100)
    priority = np.random.choice([0,1], p=[0.85,0.15])
    flexible = np.random.choice([0,1], p=[0.6,0.4])
    
    # Placeholder for predicted optimal supplier
    pred_supplier = np.nan
    
    data.append([order_id, customer_id, supplier, reliability, item, item_category, order_quantity, order_date, expected_days,
                 transport, distance, actual_days, delay, disruption, inventory, stock_risk, cost_per_unit, total_cost, priority,
                 flexible, pred_supplier])

columns = ['Order_ID','Customer_ID','Supplier_ID','Supplier_Reliability_Score','Item_ID','Item_Category','Order_Quantity',
           'Order_Date','Expected_Delivery_Days','Transport_Mode','Shipment_Distance_km','Actual_Delivery_Days','Delay',
           'Disruption_Flag','Inventory_Level','Stock_Shortage_Risk','Cost_Per_Unit','Total_Order_Cost','Customer_Priority',
           'Order_Flexibility','Predicted_Optimal_Supplier_ID']

df = pd.DataFrame(data, columns=columns)

# Save CSV safely
df.to_csv('dataset/supply_chain_full.csv', index=False)
print("Synthetic supply chain dataset generated!")