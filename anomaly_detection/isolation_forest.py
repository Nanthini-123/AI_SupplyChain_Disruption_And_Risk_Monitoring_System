from sklearn.ensemble import IsolationForest
import joblib
from preprocessing.preprocess_data import preprocess_dataset

df, le_dict, scaler = preprocess_dataset()

X = df.drop(['Delay','Disruption_Flag'], axis=1)

iso = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
iso.fit(X)
joblib.dump(iso, 'models/isolation_forest.pkl')
print("Isolation Forest model trained for anomaly detection!")