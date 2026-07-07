import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
import os
import sys
import time
import warnings
from sklearn.exceptions import ConvergenceWarning

# Suppress ConvergenceWarnings to keep the terminal output clean during animation
warnings.filterwarnings("ignore", category=ConvergenceWarning)

def train_model():
    """
    Trains a Logistic Regression model (via SGDClassifier) on the PIMA Indians Diabetes Dataset.
    It standardizes the features, trains the model with animated progress, and exports the 
    learned parameters (weights, biases, means, scales) to a CSV for lightweight inference.
    """
    data_path = "diabetes.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
        
    # 1. Load the dataset using Pandas
    df = pd.read_csv(data_path)
    X = df.drop("Outcome", axis=1) # Features (Glucose, BMI, etc.)
    y = df["Outcome"]              # Target (0 = No Diabetes, 1 = Diabetes)
    features = list(X.columns)
    
    # 2. Split into training (80%) and testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 3. Standardize the features (z-score normalization)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Initialize the Logistic Regression model using Stochastic Gradient Descent
    model = SGDClassifier(
        loss="log_loss",           # log_loss enables logistic regression and probability outputs
        max_iter=1,                # 1 iteration per epoch for manual progress tracking
        warm_start=True,           # Keep weights from previous epochs
        random_state=42,
        learning_rate="optimal",
    )
    
    epochs = 100
    # 5. Train the model iteratively to display a terminal animation
    for epoch in range(epochs):
        model.fit(X_train_scaled, y_train)
        acc = model.score(X_test_scaled, y_test)
        
        # Terminal Progress Bar Animation
        progress = int((epoch + 1) / epochs * 30)
        bar = "█" * progress + "-" * (30 - progress)
        sys.stdout.write(f"\rTraining Model: [{bar}] Epoch {epoch+1}/{epochs} | Accuracy: {acc:.4f}")
        sys.stdout.flush()
        time.sleep(0.02) # Artificial delay for visual effect
        
    print() # Add a newline after the animation finishes
    
    # 6. Evaluate the final model
    final_accuracy = model.score(X_test_scaled, y_test)
    print(f"Final Model Accuracy: {final_accuracy:.4f}")
    
    # 7. Extract learned parameters
    weights = model.coef_[0]
    bias = model.intercept_[0]
    means = scaler.mean_
    scales = scaler.scale_
    
    # 8. Package parameters into a DataFrame for export
    params_data = {
        "Feature": ["Intercept"] + features,
        "Weight": [bias] + list(weights),
        "Mean": [0.0] + list(means),
        "Scale": [1.0] + list(scales),
    }
    params_df = pd.DataFrame(params_data)
    
    # 9. Save to CSV so the Flask backend can run inference without loading heavy .pkl files
    csv_out_path = "model_parameters.csv"
    params_df.to_csv(csv_out_path, index=False)
    print(f"Model parameters saved to {csv_out_path}")


if __name__ == "__main__":
    train_model()
