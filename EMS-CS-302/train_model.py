import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import pickle
import os

# Create models directory if it doesn't exist
os.makedirs('./models', exist_ok=True)
os.makedirs('./models/analysis', exist_ok=True)

# Load dataset          
df = pd.read_csv('./datasets/patient/marikina_patients_ml.csv')

# Select features and target
X = df[['latitude', 'longitude', 'severity', 'condition', 'distance_to_hospital_km', 'response_time_min']].copy()
y = df['hospital_id']

# Encode categorical variables
le_severity = LabelEncoder()
le_condition = LabelEncoder()
X['severity'] = le_severity.fit_transform(X['severity'])
X['condition'] = le_condition.fit_transform(X['condition'])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model with best parameters from previous runs
model = RandomForestClassifier(n_estimators=200, max_depth=None, min_samples_split=2, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.2f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance)

# Cross-validation
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"Cross-validation accuracy: {cv_scores.mean():.2f} ± {cv_scores.std():.2f}")

# # Save model and encoders
# with open('./models/hospital_prediction_model.pkl', 'wb') as f:
#     pickle.dump(model, f)
# with open('./models/le_severity.pkl', 'wb') as f:
#     pickle.dump(le_severity, f)
# with open('./models/le_condition.pkl', 'wb') as f:
#     pickle.dump(le_condition, f)

# # Confusion Matrix
# cm = confusion_matrix(y_test, y_pred)
# plt.figure(figsize=(10, 8))
# disp = ConfusionMatrixDisplay(confusion_matrix=cm)
# disp.plot(xticks_rotation=45)
# plt.title('Hospital Prediction Confusion Matrix')
# plt.tight_layout()
# plt.savefig('./models/analysis/confusion_matrix.png')
# plt.close()

# print("Model training complete. Saved as hospital_prediction_model.pkl")

# Calculate model reproduction rate
df_pred = df.copy()
df_pred['predicted_hospital_id'] = model.predict(X)
match_count = (df_pred['hospital_id'] == df_pred['predicted_hospital_id']).sum()
total_count = len(df_pred)
match_percentage = (match_count / total_count) * 100
print(f"\nModel reproduces {match_percentage:.2f}% of the original hospital assignments")