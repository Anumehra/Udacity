import numpy as np
import pandas
import statsmodels.api as sm
import scipy
import matplotlib.pyplot as plt

"""
In this question, you need to:
1) implement the linear_regression() procedure
2) Select features (in the predictions procedure) and make predictions.

"""

def create_dataframe(filename):
    subway_data = pandas.read_csv(filename)
    #print subway_data.columns
    return subway_data

def normalize_features(features):
    ''' 
    Returns the means and standard deviations of the given features, along with a normalized feature
    matrix.
    ''' 
    means = np.mean(features, axis=0)
    std_devs = np.std(features, axis=0)
    normalized_features = (features - means) / std_devs
    return means, std_devs, normalized_features

def recover_params(means, std_devs, norm_intercept, norm_params):
    ''' 
    Recovers the weights for a linear model given parameters that were fitted using
    normalized features. Takes the means and standard deviations of the original
    features, along with the intercept and parameters computed using the normalized
    features, and returns the intercept and parameters that correspond to the original
    features.
    ''' 
    intercept = norm_intercept - np.sum(means * norm_params / std_devs)
    params = norm_params / std_devs
    return intercept, params

def linear_regression(features, values):
    """
    Perform linear regression given a data set with an arbitrary number of features.
    """
    features = sm.add_constant(features)
    #print features.corr()
    model = sm.OLS(values, features)
    result = model.fit()
    print result.summary()
    #print result.params
    intercept = result.params[0]
    params = result.params[1:]
    
    return intercept, params

def predictions(dataframe):
    '''
    The NYC turnstile data is stored in a pandas dataframe called weather_turnstile.
    Using the information stored in the dataframe, let's predict the ridership of
    the NYC subway using linear regression with gradient descent.
    
    You can download the complete turnstile weather dataframe here:
    https://www.dropbox.com/s/meyki2wl9xfa7yk/turnstile_data_master_with_weather.csv    
    
    Your prediction should have a R^2 value of 0.40 or better.
    You need to experiment using various input features contained in the dataframe. 
    We recommend that you don't use the EXITSn_hourly feature as an input to the 
    linear model because we cannot use it as a predictor: we cannot use exits 
    counts as a way to predict entry counts. 
    
    Note: Due to the memory and CPU limitation of our Amazon EC2 instance, we will
    give you a random subet (~10%) of the data contained in 
    turnstile_data_master_with_weather.csv. You are encouraged to experiment with 
    this exercise on your own computer, locally. If you do, you may want to complete
    Exercise 8 using gradient descent, or limit your number of features to 10 or so,
    since ordinary least squares can be very slow for a large number of features.
    
    If you receive a "server has encountered an error" message, that means you are 
    hitting the 30-second limit that's placed on running your program. Try using a
    smaller number of features.
    '''
    # Select Features (try different features!)
    features = dataframe[['hour', 'weekday', 'rain', 'meantempi']]

    # Add conds to features using dummy variables
    dummy_conds = pandas.get_dummies(dataframe['conds'], prefix='conds')
    features = features.join(dummy_conds)
    features.drop(['conds_Clear'], axis = 1, inplace = True)

    # Add UNIT to features using dummy variables
    dummy_unit = pandas.get_dummies(dataframe['UNIT'], prefix='unit')
    features = features.join(dummy_unit)
    features.drop(['unit_R003'], axis = 1, inplace = True)

    #Feature Normaization
    means, std_devs, normalized_features = normalize_features(features)

    # Values
    values = dataframe['ENTRIESn_hourly']
    
    # Get the numpy arrays
    #normalized_features = normalized_features.values
    #values = values.values
    
    # Perform linear regression
    norm_intercept, norm_params = linear_regression(normalized_features, values)

    # Recover params
    intercept, params = recover_params(means, std_devs, norm_intercept, norm_params)
    
    #Predictions
    predictions = intercept + np.dot(features, params)
    return values, predictions

def plot_residuals(values, predictions):
    '''
    Using the same methods that we used to plot a histogram of entries
    per hour for our data, why don't you make a histogram of the residuals
    (that is, the difference between the original hourly entry data and the predicted values).
    Try different binwidths for your histogram.

    Based on this residual histogram, do you have any insight into how our model
    performed?  Reading a bit on this webpage might be useful:

    http://www.itl.nist.gov/div898/handbook/pri/section2/pri24.htm
    '''
    
    plt.figure()
    #values - predictions).hist(bins = 100)
    plt.scatter(predictions, (values - predictions))
    #plt.scatter(predictions, values)
    plt.title('Residual Plot', fontsize=20, horizontalalignment='center')
    plt.ylabel('Residuals', fontsize=15)
    plt.xlabel('Predicted Values', fontsize=15)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    subway_dataframe = create_dataframe('turnstile_weather_v2.csv')
    rm_values, rm_predictions = predictions(subway_dataframe)
    plot_residuals(rm_values, rm_predictions)