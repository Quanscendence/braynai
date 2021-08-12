import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from django.core.files.storage import default_storage
import joblib


class Kmeans:
	def __init__(self,df):
		self.df = df
	def kmeans_algo(self,clusters,end_point):
		df = self.df
		scaler = StandardScaler()
		scaled_data = scaler.fit_transform(df)
		pca = PCA(n_components=2)    
		x_pca = pca.fit_transform(scaled_data)    
		new_data = pd.DataFrame(x_pca)
		clusters=int(clusters)
		km = KMeans(n_clusters = clusters)
		predictions = km.fit_predict(new_data)

   	 	# Vishwa Code below
		model_file_name= 'ml_model_'+str(end_point.name)+'_'+str(end_point.pk)+'.pkl'
		file_exists = default_storage.exists(model_file_name)
		if file_exists:
			default_storage.delete(model_file_name)
		file = default_storage.open(model_file_name,'w')
		joblib.dump(km, file)
		
		file.close()
		file_size = default_storage.size(model_file_name)
		data = {'model_file_name':model_file_name,'file_size':file_size}
		print("the predictions from clustering",data)
		return data



	def prediction_algo(self,model_file_name):
		X_test = self.df
		file = default_storage.open(model_file_name,'r')
		ml = joblib.load(file)
		# Use the loaded model to make predictions 
		predictions = ml.predict(X_test)
		return predictions