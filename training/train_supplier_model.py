import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Ensure models folder exists
os.makedirs('../models', exist_ok=True)

# Load dataset
df = pd.read_csv('../preprocessing/processed_data.csv')

# ---------------------------
# FIX DATE ISSUE 🔥
# ---------------------------
if 'Order_Date' in df.columns:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    df['Order_Year'] = df['Order_Date'].dt.year
    df['Order_Month'] = df['Order_Date'].dt.month
    df['Order_Day'] = df['Order_Date'].dt.day
    df.drop('Order_Date', axis=1, inplace=True)

# ---------------------------
# Features & Target
# ---------------------------
y = df['Supplier_ID']

X = df.drop(['Supplier_ID','Delay','Disruption_Flag','Order_ID','Customer_ID'], axis=1)

# ---------------------------
# TRAIN MODEL
# ---------------------------
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# ---------------------------
# SAVE MODEL
# ---------------------------
joblib.dump(model, '../models/supplier_model.pkl')

print("✅ Supplier model trained & saved successfully!")