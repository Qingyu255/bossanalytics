# Importing Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR

# Data Preprocessing
data = pd.read_excel("data/merged_file.xls")
print(f"Unfiltered Number of rows: {data.shape[0]}")

# Handling missing data: Remove rows with "Median Bid" equal to 0 or empty "Instructor" column
filtered_data = data.drop(data[(data["Median Bid"] == 0) | (data["Instructor"].fillna("") == "") | (data["Session"] != "Regular Academic Session")].index)

# Remove rows where "Bidding Window" contains the word "exchange"
filtered_data = filtered_data[~filtered_data["Bidding Window"].str.contains("exchange", case=False)]
filtered_data = filtered_data[~filtered_data["Bidding Window"].str.contains("1A", case=False)]
filtered_data = filtered_data[~filtered_data["Bidding Window"].str.contains("1B", case=False)]
filtered_data = filtered_data[~filtered_data["Bidding Window"].str.contains("2A", case=False)]
filtered_data = filtered_data[~filtered_data["Bidding Window"].str.contains("2B", case=False)]
filtered_data = filtered_data[~filtered_data["Bidding Window"].str.contains("Freshmen", case=False)]
# Add "Successful Bids Column which is the subtraction of values in Before Process Vacancy and After Process Vacancy"
filtered_data["Successful Bids"] = filtered_data["Before Process Vacancy"] - filtered_data["After Process Vacancy"]

# filtered_data = filtered_data.reset_index(drop=True)

filtered_data.drop(columns=["Description", "D.I.C.E", "Section"], inplace=True)
print(f"Filtered Number of rows: {filtered_data.shape[0]}, Filtered Number of columns: {filtered_data.shape[1]}")

#  Identify the indices of the columns to be one-hot encoded. We will onehot encode using pd.get(dummies)
columns_to_encode = ["Term", "Session", "Bidding Window", "Course Code", "Instructor", "School/Department"]

# One-hot encode the columns_to_encode
for column in columns_to_encode:
    window_dummies = pd.get_dummies(filtered_data[column], prefix=column)
    # Concatenate the one-hot encoded columns with the original DataFrame
    filtered_data = pd.concat([filtered_data, window_dummies], axis=1)
    # Drop the original "Bidding Window" column
    filtered_data.drop(column, axis=1, inplace=True)
    # inplace is such that it is dropped from the filtered_data df

# # My own data exploration
# encodes = filtered_data['Bidding Window Ordinal'].values
# unique_codes = []
# for code in encodes:
#     if code not in unique_codes:
#         unique_codes.append(code)
#
# print(unique_codes, len(unique_codes))

# unique_windows = []
# for window in filtered_data['Bidding Window'].values:
#     if window not in unique_windows:
#         unique_windows.append(window)
# print(unique_windows, len(unique_windows))
# # My own data exploration ^



# Explore current columns:
for i, column in enumerate(filtered_data.columns):
    print(f"{i}: {column}")

x = filtered_data.drop(columns=["Min Bid", "Median Bid"]).values
print(f"After drop 2 cols: Filtered Number of rows: {filtered_data.shape[0]}, Filtered Number of columns: {filtered_data.shape[1]}")

y = filtered_data[["Median Bid"]].values
print(x)
print(y)
print(".ravel()")
print(y.ravel())
# split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1)

# print("X_train shape:", X_train.shape)
# print("X_test shape:", X_test.shape)
# print("y_train shape:", y_train.shape)
# print("y_test shape:", y_test.shape)

# Feature Scaling:
# We will use standardisation

# # Feature Scaling: not necessary cause of all the onehot encoding we have done
# standard_scaler = StandardScaler()
# X_train = standard_scaler.fit_transform(X_train)
# X_test = standard_scaler.fit_transform(X_test)

#print(X_train)
#print(X_test)

# # Training the linear regression model
# linear_regressor = LinearRegression()
# linear_regressor.fit(x, y)
# # linear_regressor.fit(X_train, y_train)
# # y_pred = linear_regressor.predict(X_test)
# # np.set_printoptions(precision=2)
# # print(np.concatenate((y_pred.reshape(len(y_pred), 1), y_test.reshape(len(y_test), 1)), 1))
#
# Training the polynomial linear regression model
# poly_regressor = PolynomialFeatures(degree=1)
# X_poly = poly_regressor.fit_transform(X_train)
# linear_regressor_2 = LinearRegression()
# linear_regressor_2.fit(X_train, y_train)
# y_lr2_pred = linear_regressor_2.predict(X_test)
# print(f"MLR: {r2_score(y_test, y_lr2_pred)}")

# Visualising the linear regression model:
# plt.scatter(x, y, color="red")
# plt.plot(x, linear_regressor_2.predict(X_poly), color="blue")
# plt.title("Polynomial regression model")
# plt.xlabel("Features")
# plt.ylabel("Median Bid")
# plt.show()

# Decision Tree:
# dt_regressor = DecisionTreeRegressor(random_state=22)
# dt_regressor.fit(X_train, y_train)
# dt_regressor.fit(X_train, y_train)
# dt_y_pred = dt_regressor.predict(X_test)
# np.set_printoptions(precision=2)
# print(np.concatenate((dt_y_pred.reshape(len(dt_y_pred),1), y_test.reshape(len(y_test),1)),1))
# print(f"{r2_score(y_test, dt_y_pred)}")

# Random forest:
rf_regressor = RandomForestRegressor(n_estimators=10, random_state=0)
rf_regressor.fit(X_train, y_train.ravel())
y_rf_pred = rf_regressor.predict(X_test)


print(f"RFR: {r2_score(y_test, y_rf_pred)}")
