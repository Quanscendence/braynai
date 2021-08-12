import pandas as pd
import numpy as np
import sklearn
import autosklearn.classification as classifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from django.core.files.storage import default_storage
import joblib


# AutoMl Class
class AutoMl:
	def __init__(self,df):
		self.df = df
	def auto_algo(self,target,end_point):
	    df = self.df
	    X = df.drop([target],axis=1)
	    y = df[target]
	    # print("algorithm tryning started",y)
	    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
	    # print("data splited ")
	    automl = classifier.AutoSklearnClassifier(time_left_for_this_task=180,per_run_time_limit=30)
	    # print("instance created")
	    automl.fit(X_train,y_train)
	    # print("ml fited")
	    predictions = automl.predict(X_test)
	    # print("algorithm tryning ended")

	    accuracy = int(accuracy_score(y_test,predictions)*100)
	    show = automl.show_models()
	    # Vishwa Code below

	    # Save model file
	    model_file_name= 'ml_model_'+str(end_point.name)+'_'+str(end_point.pk)+'.pkl'

	    file_exists = default_storage.exists(model_file_name)
	    if file_exists:
	    	default_storage.delete(model_file_name)
	    file = default_storage.open(model_file_name,'wb')
	    # Save the model as a pickle in a file
	    joblib.dump(automl, file)

	    file.close()
	    file_size = default_storage.size(model_file_name)


	    # End of file save

	    data = {'accuracy':accuracy,'model_file_name':model_file_name,'file_size':file_size}
	    # print(data)
	    return data
	def prediction_algo(self,model_file_name):
		X_test = self.df
		file = default_storage.open(model_file_name,'rb')
		ml = joblib.load(file)
		# Use the loaded model to make predictions
		predictions = ml.predict(X_test)
		return predictions
