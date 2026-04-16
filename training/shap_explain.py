import shap
import joblib
import pandas as pd
from preprocessing.preprocess_data import preprocess_dataset

df, le_dict, scaler = preprocess_dataset()
X = df.drop(['Delay','Disruption_Flag'], axis=1)

model = joblib.load('models/random_forest_delay.pkl')

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Save explainer for Streamlit
joblib.dump(explainer, 'models/shap_explainer.pkl')
print("SHAP explainer saved!")