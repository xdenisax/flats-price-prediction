
import pandas as pd
import numpy as np
from scipy import stats 
from sklearn import preprocessing
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV

# Reading crawled data 
data = pd.read_json('/Users/calot/Repositories/wmad/realEstates/realestate/realestate/out.json')

# Filling nulls and getting data ready
data = data.ffill(axis ='rows').bfill(axis ='rows') 
data["surface"] = [float(str(i).replace(",", ".")) for i in data["surface"]]
data['price'] = data['price'].str.replace('.','').astype(float)

# Reading and getting prediction input ready
to_predict = pd.read_json('/Users/calot/Repositories/wmad/realEstates/realestate/toPredict.json')
to_predict["surface"] = [float(str(i).replace(",", ".")) for i in to_predict["surface"]]

# Filtering data by location of the input
locationToPredict = to_predict['location'][0]
data = data.query("location == @locationToPredict")

# Detect and remove outliers 
z = np.abs(stats.zscore(data['price']))
data = data.drop(data[z > 3].index)

# Encoding qualitative data to numeric data 
le = preprocessing.LabelEncoder()
for name in data.columns: 
    if pd.api.types.is_string_dtype(data[name]): 
        data[name] = data[name].astype(str)
        le.fit(data[name])
        data[name] = le.transform(data[name])
        
for name in to_predict.columns: 
    if pd.api.types.is_string_dtype(to_predict[name]): 
        to_predict[name] = to_predict[name].astype(str)
        le.fit(to_predict[name])
        to_predict[name] = le.transform(to_predict[name])

# Keep only top price correlated features of a flat 
top_features = data.corr()[['price']].sort_values(by=['price'],ascending=False).index[:5]
data = data[top_features]
to_predict = to_predict[top_features[1:6]]

# Regression variables  
X = data[top_features[1:5]]
Y = data['price']

# Multi-layer Perceptron regressor with a 
mlp=MLPRegressor(random_state=42)
mlp_param = {
    'hidden_layer_sizes': [(273,230,30), (273,230,20), (273,230,50)], # number of neurons per layer
    'activation': ['tanh'], #hyperbolic tangent -
    'solver': ['sgd'], # stochastic gradient descent.
    'alpha': [0.0001],
    'learning_rate': ['constant'],   #constant learning rate 
}

# Apply GridSearchCV
# Searching over specified parameter values for an estimator.
# Params are optimized by cross-validated grid-search over a parameter grid.
mlp_grid = GridSearchCV(mlp,
                        mlp_param, # param_grid 
                        cv = 5, # the cross-validation splitting strategy - number of folds 
                        n_jobs = 3, #jobs number run in parallel 
                        verbose=True)
mlp_grid.fit(X,Y)

#Apply MLPRegressor with same params as GridSearchCV 
mlp_model=MLPRegressor(activation= 'tanh',
                 alpha=0.0001, 
                 hidden_layer_sizes=(273, 230, 30),
                 learning_rate= 'adaptive', 
                 solver= 'sgd')
#Fitting data
mlp_model.fit(X, Y)
#Estimating input 
mlp_prediction = mlp_model.predict(to_predict)

print("Estimated price:", round(mlp_prediction[0],0))








#   {"location": " Prelungirea Ghencea", "rooms": "2", "surface": "60", "confort": "1", "separation": "semidecomandat", "floor": "2", "kitchensNo": "1", "bathroomsNo": "1", "year": "2018", "balconiesNo": "1"}
# 65.300
#   {"location": " Militari", "rooms": "1", "surface": "38", "confort": "1", "separation": "decomandat", "floor": "3", "kitchensNo": "1", "bathroomsNo": "1", "year": "2020", "balconiesNo": "1"}
# 52.200 / 63.615
#   {"location": " Theodor Pallady", "rooms": "2", "surface": "45,55", "confort": 1, "separation": "decomandat", "floor": "1", "kitchensNo": "1", "bathroomsNo": "1", "year": "2022", "balconiesNo": "1"}
# 73.000 / 80.479
#     {"location": " Floreasca", "rooms": "3", "surface": "85,63", "confort": "1", "separation": "semidecomandat", "floor": "1", "kitchensNo": "1", "bathroomsNo": "2", "year": "2021", "balconiesNo": "1"}
# 425.000 / 444.715
#  {"location": " Cr\u00e2nga\u015fi", "rooms": "2", "surface": "60", "confort": "1", "separation": "decomandat", "floor": "2", "kitchensNo": "1", "bathroomsNo": "1", "year": "1980", "balconiesNo": "0"}
# 89.074
