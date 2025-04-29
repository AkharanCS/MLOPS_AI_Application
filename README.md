# Spam Shield - CH21B009

## Directories
- **backend**: contains all the codes and configurations required for Part-A of the assignment.
- **frontend**: contains all the codes and configurations required for Part-B of the assignment.
- **model_training**: contains all the codes and configurations required for Part-B of the assignment.

## Files in backend
- **`backend_api.py`**: contains the fastAPI endpoints (predict and retrain)
- **`predict.py`**: contains the predict function which is imported in the backend.
- **`retrain_model.py`**: contains the retrain function which is imported in the backend.
- **`Dockerfile`**: contains the docker file which was used for building the backend docker image.

## Files in frontend
- **`frontend.py`**: contains the script for streamlit frontend in which backend API is called upon.
- **`extract_email.py`**: contains the get_emails() and move_to_spam() functions imported in frontend. 
- **`Dockerfile`**: contains the docker file which was used for building the frontend docker image.
- **`credentials.yaml`**: contains the gmail login credentials.

## Files in model_training
- **`mlflow_sweep.py`**: contains the script with which mlflow runs were made.
- **`spam_classification_sk.ipynb`**: notebook containing a detailed training process of the model. 

## Other Important files
- **`docker-compose.yaml`**: file that has be run to start all the five docker containers.
- **`prometheus.yml`**: contains the scrape configuration for prometheus container.
- **`requirements.txt`**: contains all the libraries and dependancies required for both frontend and backend.
