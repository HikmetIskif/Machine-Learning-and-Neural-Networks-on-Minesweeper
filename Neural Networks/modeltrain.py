import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model
import joblib

# veriyi yukle
data = pd.read_csv("minesweeper_data.csv")

if data.isnull().values.any():
    print("Data contains missing values. Cleaning data...")
    data = data.dropna()

X = data.iloc[:, :-1].values  # Features
y = data.iloc[:, -1].values   # Labels

# veriyi ayir
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# normalize et
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# yapay sinir aglarini kur
model = Sequential()
model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# modeli egit
model.fit(X_train, y_train, epochs=50, batch_size=10, validation_data=(X_test, y_test))

# kaydet
model.save("minesweeper_nn_model.h5")
joblib.dump(scaler, "scaler.pkl")

_, accuracy = model.evaluate(X_test, y_test)
print(f"Model accuracy: {accuracy}")
