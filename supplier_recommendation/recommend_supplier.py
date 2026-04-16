import pandas as pd
import numpy as np

def recommend_supplier(order_row, supplier_reliability):
    """
    Recommend an alternate supplier if the current one is risky
    """
    current_supplier = order_row['Supplier_ID']
    current_reliability = supplier_reliability.get(current_supplier, 50)
    
    # If reliability < 75%, find better supplier with same category
    if current_reliability < 75:
        better = {k:v for k,v in supplier_reliability.items() if v >= 75}
        if better:
            recommended = max(better, key=better.get)
            return recommended
    return current_supplier