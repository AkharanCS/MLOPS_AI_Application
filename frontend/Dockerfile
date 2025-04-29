FROM python:3.10

WORKDIR /frontend

COPY . /frontend

RUN pip install -r requirements.txt

EXPOSE 8501

# Run the frontend (Streamlit)
CMD ["streamlit", "run", "frontend.py"]