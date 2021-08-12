import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from django.core.files.storage import default_storage
import joblib 


class Linear:
	def __init__(self,df):
		self.df = df
	def linear_model(self,target,end_point):
	    df = self.df
	    print("the ml df is ",df)
	    X = df.drop([target],axis=1)
	    y = df[target]
	    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
	    lm = LinearRegression()
	    lm.fit(X_train,y_train)
	    predictions = lm.predict(X_test)
	    accuracy = {'MAE':metrics.mean_absolute_error(y_test, predictions),'MSE':metrics.mean_squared_error(y_test, predictions),'RMSE':np.sqrt(metrics.mean_squared_error(y_test, predictions))}
	    # Vishwa Code below

	    # Save model file
	    model_file_name= 'ml_model_'+str(end_point.name)+'_'+str(end_point.pk)+'.pkl'

	    file_exists = default_storage.exists(model_file_name)
	    if file_exists:
	    	default_storage.delete(model_file_name)

	    
	    file = default_storage.open(model_file_name,'wb')
	    print("the content is ")
	    # Save the model as a pickle in a file 
	    joblib.dump(lm, file)
	    
	    file.close()
	    file_size = default_storage.size(model_file_name)
	    print("file size is ",file_size)
	    # End of file save

	    data = {'accuracy':accuracy,'model_file_name':model_file_name,'file_size':file_size}

	    print(data)
	    return data

	def prediction_algo(self,model_file_name):
		X_test = self.df
		file = default_storage.open(model_file_name,'rb')
		ml = joblib.load(file)
		# Use the loaded model to make predictions 
		predictions = ml.predict(X_test)
		return predictions




