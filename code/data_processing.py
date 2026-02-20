import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
import joblib
import os

# ─── 1. CHARGEMENT ───────────────────────────────────────────
print("=" * 55)
print("   PIPELINE DE PREPROCESSING - NURSERY DATASET")
print("=" * 55)

df = pd.read_csv('data/raw/nursery.csv')
print(f"\n[1] Dataset charge : {df.shape[0]} lignes, {df.shape[1]} colonnes")

# ─── 2. SEPARATION FEATURES / CIBLE ──────────────────────────
X = df.drop(columns=['class'])
y = df['class']

print(f"[2] Features : {list(X.columns)}")
print(f"    Cible    : 'class' ({y.nunique()} classes)")

# ─── 3. DEFINITION DES VALEURS ORDINALES ─────────────────────
# Ordre logique pour chaque variable categorielle
ordinal_categories = [
    ['great_pret', 'pretentious', 'usual'],                          # parents
    ['very_crit', 'critical', 'improper', 'less_proper', 'proper'], # has_nurs
    ['foster', 'incomplete', 'completed', 'complete'],               # form
    ['1', '2', '3', 'more'],                                         # children
    ['critical', 'less_conv', 'convenient'],                         # housing
    ['inconv', 'convenient'],                                         # finance
    ['problematic', 'slightly_prob', 'nonprob'],                     # social
    ['not_recom', 'recommended', 'priority'],                        # health
]

features = list(X.columns)

# ─── 4. ENCODAGE ──────────────────────────────────────────────
encoder = OrdinalEncoder(
    categories=ordinal_categories,
    handle_unknown='use_encoded_value',
    unknown_value=-1
)

X_encoded = encoder.fit_transform(X)
X_encoded = pd.DataFrame(X_encoded, columns=features)

print(f"\n[3] Encodage OrdinalEncoder applique")
print(f"    Exemple apres encodage :")
print(X_encoded.head(3).to_string())

# ─── 5. ENCODAGE DE LA CIBLE ──────────────────────────────────
class_order = ['not_recom', 'recommend', 'very_recom', 'priority', 'spec_prior']
label_encoder = OrdinalEncoder(categories=[class_order])
y_encoded = label_encoder.fit_transform(y.values.reshape(-1, 1)).ravel().astype(int)

print(f"\n[4] Encodage cible :")
for i, cls in enumerate(class_order):
    count = (y_encoded == i).sum()
    print(f"    {i} = {cls:<12} ({count} instances)")

# ─── 6. SPLIT TRAIN / TEST STRATIFIE ──────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

print(f"\n[5] Split stratifie 80/20 :")
print(f"    Train : {X_train.shape[0]} instances")
print(f"    Test  : {X_test.shape[0]} instances")

# ─── 7. SMOTE SUR TRAIN UNIQUEMENT ───────────────────────────
print(f"\n[6] Distribution AVANT SMOTE (train) :")
unique, counts = np.unique(y_train, return_counts=True)
for u, c in zip(unique, counts):
    print(f"    {class_order[u]:<15} : {c}")

smote = SMOTE(random_state=42, k_neighbors=1)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

print(f"\n[7] Distribution APRES SMOTE (train) :")
unique, counts = np.unique(y_train_resampled, return_counts=True)
for u, c in zip(unique, counts):
    print(f"    {class_order[u]:<15} : {c}")

print(f"\n    Train AVANT SMOTE : {X_train.shape[0]} instances")
print(f"    Train APRES SMOTE : {X_train_resampled.shape[0]} instances")

# ─── 8. SAUVEGARDE DES DONNEES ────────────────────────────────
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/models/encoders', exist_ok=True)

# Données
pd.DataFrame(X_train_resampled, columns=features).to_csv('data/processed/X_train.csv', index=False)
pd.DataFrame(X_test, columns=features).to_csv('data/processed/X_test.csv', index=False)
pd.Series(y_train_resampled, name='class').to_csv('data/processed/y_train.csv', index=False)
pd.Series(y_test, name='class').to_csv('data/processed/y_test.csv', index=False)

print(f"\n[8] Donnees sauvegardees dans data/processed/")

# Encodeurs
joblib.dump(encoder, 'data/models/encoders/feature_encoder.pkl')
joblib.dump(label_encoder, 'data/models/encoders/label_encoder.pkl')
joblib.dump(class_order, 'data/models/encoders/class_order.pkl')

print(f"[9] Encodeurs sauvegardes dans data/models/encoders/")

print(f"""
+=====================================================+
|         PREPROCESSING TERMINE AVEC SUCCES         |
+=====================================================+
|  X_train (apres SMOTE) : {X_train_resampled.shape[0]} instances          
|  X_test                : {X_test.shape[0]} instances           
|  Encodeurs             : sauvegardes (.pkl)        
|  Desequilibre          : corrige par SMOTE         
+=====================================================+
""")