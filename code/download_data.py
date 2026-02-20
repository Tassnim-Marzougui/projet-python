import pandas as pd
import os

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/nursery/nursery.data"

columns = ['parents', 'has_nurs', 'form', 'children', 
           'housing', 'finance', 'social', 'health', 'class']

print("Téléchargement du dataset...")
df = pd.read_csv(url, header=None, names=columns)

os.makedirs('data/raw', exist_ok=True)
df.to_csv('data/raw/nursery.csv', index=False)

print(f"✅ Dataset téléchargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
print("\nAperçu :")
print(df.head())
print("\nDistribution de la cible :")
print(df['class'].value_counts())
