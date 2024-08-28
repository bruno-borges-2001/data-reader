from datetime import datetime
from pandas import DataFrame
import os

def export_data(destination: str, data: list):
    filename = f'export-{datetime.now().isoformat()}.csv'
    path = os.path.join(destination, filename)
    
    df = DataFrame().from_records(data)
    df.to_csv(path, sep=';')
    
    return path