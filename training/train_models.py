import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import joblib

# ---------------------------
# Root folder models path
# ---------------------------
root_models_dir = '../models'  # relative to training/
os.makedirs(root_models_dir, exist_ok=True)

# ---------------------------
# Load preprocessed dataset
# ---------------------------
df = pd.read_csv('../preprocessing/processed_data.csv')  # Adjust path if needed

# ---------------------------
# Handle date column
# ---------------------------
if 'Order_Date' in df.columns:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    df['Order_Year'] = df['Order_Date'].dt.year
    df['Order_Month'] = df['Order_Date'].dt.month
    df['Order_Day'] = df['Order_Date'].dt.day
    df.drop('Order_Date', axis=1, inplace=True)

# ---------------------------
# Features and target
# ---------------------------
drop_cols = ['Delay', 'Disruption_Flag', 'Predicted_Optimal_Supplier_ID', 'Order_ID', 'Customer_ID']
X = df.drop(drop_cols, axis=1)
y_delay = df['Delay']
y_disruption = df['Disruption_Flag']

print("Feature types:\n", X.dtypes)

# ---------------------------
# Split for Delay Prediction
# ---------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y_delay, test_size=0.2, random_state=42)

# ---------------------------
# Train Random Forest for Delay
# ---------------------------
rf_delay = RandomForestClassifier(n_estimators=100, random_state=42)
rf_delay.fit(X_train, y_train)
joblib.dump(rf_delay, os.path.join(root_models_dir, 'rf_delay_model.pkl'))
print("Random Forest Delay Model trained and saved in root models folder.")

# ---------------------------
# Train XGBoost for Delay (optional)
# ---------------------------
xgb_delay = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
xgb_delay.fit(X_train, y_train)
joblib.dump(xgb_delay, os.path.join(root_models_dir, 'xgb_delay_model.pkl'))
print("XGBoost Delay Model trained and saved in root models folder.")

# ---------------------------
# Train Random Forest for Disruption
# ---------------------------
X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(X, y_disruption, test_size=0.2, random_state=42)
rf_disruption = RandomForestClassifier(n_estimators=100, random_state=42)
rf_disruption.fit(X_train_d, y_train_d)
joblib.dump(rf_disruption, os.path.join(root_models_dir, 'rf_disruption_model.pkl'))
print("Random Forest Disruption Model trained and saved in root models folder.")
print("TRAIN FEATURES:", list(X.columns))