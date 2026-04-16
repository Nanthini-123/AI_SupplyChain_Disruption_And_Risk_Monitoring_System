# preprocess_data.py
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

# ---------------------------
# Ensure 'preprocessing' and 'models' folders exist
# ---------------------------
os.makedirs('preprocessing', exist_ok=True)
os.makedirs('models', exist_ok=True)

# ---------------------------
# Load raw dataset
# ---------------------------
df = pd.read_csv('../dataset/supply_chain_full.csv')  # adjust path if needed

# ---------------------------
# Handle missing values
# ---------------------------
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].fillna('Unknown')

for col in df.select_dtypes(include=['float64', 'int64']).columns:
    df[col] = df[col].fillna(0)

# ---------------------------
# Convert date columns
# ---------------------------
if 'Order_Date' in df.columns:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    df['Order_Year'] = df['Order_Date'].dt.year
    df['Order_Month'] = df['Order_Date'].dt.month
    df['Order_Day'] = df['Order_Date'].dt.day
    df.drop('Order_Date', axis=1, inplace=True)

# ---------------------------
# Encode categorical columns
# ---------------------------
label_encoders = {}
for col in df.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Save label encoders
joblib.dump(label_encoders, 'models/label_encoders.pkl')

# ---------------------------
# Scale numeric columns
# ---------------------------
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

# Save scaler
joblib.dump(scaler, 'models/scaler.pkl')

# ---------------------------
# Save preprocessed CSV
# ---------------------------
df.to_csv('preprocessing/processed_data.csv', index=False)
print("Data preprocessing complete. Preprocessed CSV saved to 'preprocessing/processed_data.csv'.")
print("Label encoders and scaler saved in 'models/' folder.")