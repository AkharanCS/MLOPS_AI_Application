import pickle as pkl

def prediction(texts):
    # Loading the model
    with open("count_vectorizer.pkl","rb") as f:
        embed = pkl.load(f)

    with open("naive_bayes_model.pkl","rb") as f:
        model = pkl.load(f)

    # Vectorizing and predicting
    X_test_embed = embed.transform(texts)
    y_pred_NB = model.predict(X_test_embed)
    return list(y_pred_NB)




