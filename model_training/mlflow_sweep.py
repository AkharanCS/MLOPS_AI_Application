import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Loading Data
df_main = pd.read_csv("model_training/enron_spam_data.csv")
df_main.fillna("Hello",inplace=True)
df_main["Message"] = df_main["Message"].astype("str")

df_X = df_main.drop(columns="Spam/Ham",axis=1)
df_y = df_main["Spam/Ham"]

X_train,X_test,y_train,y_test = train_test_split(df_X,df_y)

# Feature Engineering
embed = CountVectorizer(max_features=20000)
X_embed_train = embed.fit_transform(X_train["Message"])
X_embed_test = embed.transform(X_test["Message"])

# Starting MLflow Experiment
mlflow.set_experiment("AI-App Hyperparameter Tuning")

# Defining hyperparameter search space
alpha_values = [0.1, 0.5, 1.0, 2.0, 5.0]

# Looping over hyperparameters
for alpha in alpha_values:
    with mlflow.start_run():
        
        # Model Training
        model = MultinomialNB(alpha=alpha)
        model.fit(X_embed_train, y_train)

        # Prediction and Evaluation
        y_pred = model.predict(X_embed_test)
        acc = accuracy_score(y_test, y_pred)

        # Log parameters, metrics, and model
        mlflow.log_param("alpha", alpha)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(model, "model")

print("Hyperparameter tuning completed.")