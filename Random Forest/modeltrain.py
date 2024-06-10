import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# veriyi yukle
data = pd.read_csv("minesweeper_data.csv")

if data.isnull().values.any():
    print("Data contains missing values. Cleaning data...")
    data = data.dropna()

X = data.iloc[:, :-1]  # Features
y = data.iloc[:, -1]   # Labels

# veriyi ayir
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# modeli egit
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# kaydet
joblib.dump(model, "minesweeper_model.pkl")

print(f"Model accuracy: {model.score(X_test, y_test)}")
