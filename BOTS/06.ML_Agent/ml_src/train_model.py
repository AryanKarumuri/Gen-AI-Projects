import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

def train_model(dataset_path, model_path):

    # Load dataset
    df = pd.read_csv(dataset_path)

    # Replace zeros with NaN for specific columns
    cols_with_zero_as_missing = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    df[cols_with_zero_as_missing] = df[cols_with_zero_as_missing].replace(0, np.nan)

    # Impute missing values
    for col in cols_with_zero_as_missing:
        df[col].fillna(df[col].median(), inplace=True)

    # Shuffle
    df = shuffle(df, random_state=42)

    # Features and target
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Define model
    rf = RandomForestClassifier(class_weight="balanced", random_state=42)

    param_dist = {
        "n_estimators": [100, 200, 300, 500],
        "max_depth": [None, 5, 10, 15, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
        "bootstrap": [True, False],
    }

    # Randomized search
    random_search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=param_dist,
        n_iter=20,
        cv=5,
        scoring="recall",
        verbose=1,
        random_state=42,
        n_jobs=-1,
    )

    random_search.fit(X_train, y_train)
    best_model = random_search.best_estimator_

    # Evaluate
    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    print("Model Evaluation:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("ROC AUC:", roc_auc_score(y_test, y_proba))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Save model
    joblib.dump(best_model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    dataset_path = "../artifacts/dataset/diabetes.csv"
    model_path = "../artifacts/model/model.pkl"
    train_model(dataset_path, model_path)
