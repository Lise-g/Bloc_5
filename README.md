# Bloc_5
**Deployment project for certification**

This project aims at :  
- building a web dashboard in order to find the best minimum delay between two rentals,
- building an online API for pricing optimization.

> Video link of the project : 👉 https://share.vidyard.com/watch/TwuEorJGJTPDF5rZG3ZPqE? 👈

Contact : Lise Gnos  
email : lise.gnos@gmail.com  

## 1/ Web dashboard

> Notebook : 'deployment/data_analysis.ipynb'  

This notebook shows the data analysis that was made in order to build the web dashboard. All the comments and the explanations of the decisions are in that file.  

> Python script : 'deployment/dashboard/app_streamlit.py'  

This script was used to build the web dashboard with Streamlit. It takes the graphs that were designed in the notebook file. As it is a dashboard, all additionnal comments were not put in there.  
The dashboard is hosted online on a Heroku server at this URL :  
https://app-streamlit-getaround.herokuapp.com/  
The source file for the analysis is hosted on an AWS S3 bucket that is publicly available at this URL :  
https://bucket-getaround-project.s3.eu-west-3.amazonaws.com/get_around_delay_analysis.xlsx  

## 2/ Online API

> Notebook : 'deployment/machine_learning.ipynb'  

This notebook was used to build the machine learning model from the csv file that was provided.  
A baseline model (simple linear regression) was made and an optimized model (xgboost regressor) was chosen.  
The xgboost model was saved as a joblib file and was used for the online API.  

> Model : 'deployment/online-API/xgbregressor.joblib'  
> Python script : 'deployment/online-API/app_fastAPI.py'  

This script was used to build the online API. It was made with FastAPI.  
The API is hosted online on a Heroku server at this URL :  
https://app-fastapi-getaround.herokuapp.com/  

> Notebook : 'deployment/request_api.ipynb'  

This notebook shows how to request the online API at the /predict endpoint with the POST method in order to get the prediction from the model.

👉 The 'deployment/src' folder contains the 2 source files (the one for the data analysis and the one for the machine learning).  
👉 The 2 apps have a Dockerfile because they were both put in a Docker container and pushed to Heroku.  

