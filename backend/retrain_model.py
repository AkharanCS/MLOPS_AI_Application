import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle as pkl

def retrain(feedback_data,feedback_labels):
    df_main = pd.read_csv("backend/enron_spam_data.csv")
    df_main.fillna("Hello",inplace=True)
    df_main["Message"] = df_main["Message"].astype("str")

    df_X = pd.concat([df_main[['Message']], pd.DataFrame({'Message': feedback_data})], ignore_index=True)
    df_y = pd.concat([df_main[['Spam/Ham']], pd.DataFrame({'Spam/Ham': feedback_labels})], ignore_index=True)

    '''
    df_X = df_main.drop(columns="Spam/Ham",axis=1)
    df_y = df_main["Spam/Ham"]
    '''
    X_train,X_test,y_train,y_test = train_test_split(df_X,df_y)

    embed = CountVectorizer(max_features=50000)
    X_embed_train = embed.fit_transform(X_train["Message"])

    model = MultinomialNB()
    model.fit(X_embed_train, y_train)

    with open('backend/naive_bayes_model.pkl', 'wb') as model_file:
        pkl.dump(model, model_file)
    
    with open('backend/count_vectorizer.pkl', 'wb') as vec_file:
        pkl.dump(embed, vec_file)

