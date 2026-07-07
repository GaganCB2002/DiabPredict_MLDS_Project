import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
import os
import sys
import time
import warnings
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)

def train_model():
    data_path = "diabetes.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
    df = pd.read_csv(data_path)
    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]
    features = list(X.columns)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    model = SGDClassifier(
        loss="log_loss",
        max_iter=1,
        warm_start=True,
        random_state=42,
        learning_rate="optimal",
    )
    epochs = 100
    for epoch in range(epochs):
        model.fit(X_train_scaled, y_train)
        acc = model.score(X_test_scaled, y_test)
        
        progress = int((epoch + 1) / epochs * 30)
        bar = "█" * progress + "-" * (30 - progress)
        sys.stdout.write(f"\rTraining Model: [{bar}] Epoch {epoch+1}/{epochs} | Accuracy: {acc:.4f}")
        sys.stdout.flush()
        time.sleep(0.02)
        
    print() # Add a newline after the animation finishes
    final_accuracy = model.score(X_test_scaled, y_test)
    print(f"Final Model Accuracy: {final_accuracy:.4f}")
    weights = model.coef_[0]
    bias = model.intercept_[0]
    means = scaler.mean_
    scales = scaler.scale_
    params_data = {
        "Feature": ["Intercept"] + features,
        "Weight": [bias] + list(weights),
        "Mean": [0.0] + list(means),
        "Scale": [1.0] + list(scales),
    }
    params_df = pd.DataFrame(params_data)
    csv_out_path = "model_parameters.csv"
    params_df.to_csv(csv_out_path, index=False)
    print(f"Model parameters saved to {csv_out_path}")


if __name__ == "__main__":
    train_model()
