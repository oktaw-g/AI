# -*- coding: utf-8 -*-
"""P3.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eFh-5JNd5KEqLhrUWsDs74trCtS-smeA

# Projekt 3
 **California Housing**

 Podział jak w przykładzie z zajęć
"""

import pandas as pd
import numpy as np

DATASET_PATH = "CaliforniaHousing.csv"

# Wczytanie datasetu California Housing
dataset = pd.read_csv(DATASET_PATH)

# Informacje o zestawie danych
dataset.info()

DATASET_FEATURE_DSCRB = {
    "longitude": "A measure of how far west a house is; a higher value is farther west",
    "latitude": "A measure of how far north a house is; a higher value is farther north",
    "housing_median_age": "Median age of a house within a block; a lower number is a newer building",
    "total_rooms": "Total number of rooms within a block",
    "total_bedrooms": "Total number of bedrooms within a block",
    "population": "Total number of people residing within a block",
    "households": "Total number of households, a group of people residing within a home unit, for a block",
    "median_income": "Median income for households within a block of houses (measured in tens of thousands of US Dollars)",
    "median_house_value": "Median house value for households within a block (measured in US Dollars)",
    "ocean_proximity": " Location of the house w.r.t ocean/sea",

}
DATASET_FEATURE_LABELS = {
    "longitude": "lon",
    "latitude": "lat",
    "housing_median_age": "age",
    "total_rooms": "rooms",
    "total_bedrooms": "bedrooms",
    "population": "pop",
    "households": "households",
    "median_income": "income",
    "median_house_value": "val",
    "ocean_proximity": "ocean",
}

# Zmiana nazwy kolumn
dataset = dataset.rename(columns=DATASET_FEATURE_LABELS)
dataset.info()

"""# Brakujące dane"""

# Znalezienie brakujących danych
dataset.isnull().any()

# W rzędzie jest brakująca wartość
isnull = dataset.isnull().any(axis=1)
print(np.count_nonzero(isnull),"brakujących wartości.")
# Usunięcie rzędu
dataset = dataset.drop(np.asarray(isnull).nonzero()[0].tolist() ,axis=0)

# Podgląd pierwszych 10 rzędów
dataset.head(10)

dataset_cat=dataset.select_dtypes(include='object')
dataset_cat.columns

dataset.replace(to_replace=["NEAR OCEAN","<1H OCEAN","NEAR BAY",'ISLAND',"INLAND"], value = [0,1,2,3,4], inplace=True)

dataset['ocean'] = dataset['ocean'].astype('int')

"""# Wydzielenie zmiennej zależnej"""

# Wydzielenie zmiennej zależnej (Y)
x,y = dataset.drop(columns=["val"]), dataset["val"]

"""# EDA"""

# Podstawowa analiza statystyczna
x.describe()

# Hisotgramy zmiennych niezależnych
x.hist(figsize=(15,10), bins=20)

# Wykresy BOXPLOT

import seaborn as sns
import matplotlib.pyplot as plt

# Zmienna zależna Y(median value) w zależności od ilości pokojów
plt.clf()
sns.boxplot(y=y, x=x["bedrooms"].round())
plt.show()

plt.clf()
sns.boxplot(y=x["bedrooms"], x=y.round(-1))
plt.show()

# Analiza korelacji pomiędzy zmiennymi

import seaborn as sns
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))

sns.heatmap(x.select_dtypes(exclude='object').corr(), ax=ax, annot=True)

"""# Podział na zbiory Train, Test i Val"""

# Podział na subsety TRAIN, TEST oraz VAL

from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.4, random_state=5, shuffle=True)
x_val, x_test, y_val, y_test = train_test_split(x_test, y_test, test_size=0.5, random_state=5, shuffle=True)

x_train.describe()

x_val.describe()

x_test.describe()

"""# Skalowanie wartości niezależnych"""

# Skalowanie zmiennych niezależnych numerycznych z użyciem StandardScaler
# Enkodowanie zmiennych niezależnych kategorycznych z użyciem OrdinalEncoder

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.compose import make_column_transformer


col_categorical = x_train.select_dtypes(include='object').columns
col_numerical = x_train.select_dtypes(exclude='object').columns

col_transformer = make_column_transformer(
    (StandardScaler(), col_numerical),
    (OrdinalEncoder(), col_categorical)
)

"""# Regresja"""

from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Regresja liniowa

from sklearn.linear_model import LinearRegression

linear_regressor = Pipeline([
    ('col_transformer', col_transformer),
    ('linear_regressor', LinearRegression(positive=True))
])
linear_regressor.fit(x_train, y_train)

y_pred = linear_regressor.predict(x_train)
print(f"RMSE: {mean_squared_error(y_train, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_train, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_train, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw treningowy")
ax.grid(True)
plt.show()

# Drzewo decyzyjne

from sklearn.tree import DecisionTreeRegressor

decision_tree = Pipeline([
    ('col_transformer', col_transformer),
    ('decision_tree', DecisionTreeRegressor())
])
decision_tree.fit(x_train, y_train)

y_pred = decision_tree.predict(x_train)
print(f"RMSE: {mean_squared_error(y_train, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_train, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_train, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw treningowy")
ax.grid(True)
plt.show()

"""# Ewaluacja"""

# Ewaluacja regresji liniowej na zestawie walidacyjnym

y_pred = linear_regressor.predict(x_val)
print(f"RMSE: {mean_squared_error(y_val, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_val, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_val, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw walidacyjny")
ax.grid(True)
plt.show()

# Ewaluacja drzewa decyzyjnego na zestawie walidacyjnym

y_pred = decision_tree.predict(x_val)
print(f"RMSE: {mean_squared_error(y_val, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_val, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_val, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw walidacyjny")
ax.grid(True)
plt.show()

"""# Strojenie hiperparametrów"""

# Listowanie parametrów drzewa decyzyjnego
decision_tree['decision_tree'].get_params()

# Dobór wielkości drzewa decyzyjnego
rmse = []
depths = [1, 2, 5, 10, 15, 20, 25, 50]
for depth in depths:

    decision_tree.set_params(**{'decision_tree__max_depth': depth})
    decision_tree.fit(x_val, y_val)
    y_pred = decision_tree.predict(x_val)
    rmse.append(mean_squared_error(y_val, y_pred)**.5)

best_depth, best_rmse = depths[np.argmin(rmse)], np.min(rmse)


print(f"Best RMSE: {best_rmse:.2f} dla max_depth={best_depth}")

# Zastosowanie hiperparametrów i ponowny trening
decision_tree.set_params(**{'decision_tree__max_depth': best_depth})

decision_tree.fit(x_train, y_train)

# Ewaluacja na zestawie walidacyjnym
y_pred = decision_tree.predict(x_val)
print(f"RMSE: {mean_squared_error(y_val, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_val, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_val, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw walidacyjny")
ax.grid(True)
plt.show()

"""# LASSO"""

# Regresja Lasso do oceny ważności zmiennych niezależnych

from sklearn.linear_model import Lasso

lasso = Pipeline([
    ('col_transformer', col_transformer),
    ('lasso', Lasso(alpha=1e-05, max_iter=4000))
])

lasso.fit(x_train, y_train)

# Wyznaczenie ważności zmiennych niezależnych i ich wizualizacja

lasso_coef = np.abs(lasso['lasso'].coef_)
lasso_coef /= np.sum(lasso_coef)

THRESH = 0.045

decision_tree_coef = np.abs(decision_tree['decision_tree'].feature_importances_)
decision_tree_coef /= np.sum(decision_tree_coef)

# plotting the Column Names and Importance of Columns.
fig,axes = plt.subplots(1,2,figsize=(10,3))

axes[0].bar(x_train.columns.values, lasso_coef)
axes[0].axhline(y=THRESH, color='r', linestyle='-')
axes[0].grid()
axes[0].set_xticks(x_train.columns.values)
axes[0].set_xticklabels(x_train.columns.values, rotation = 90)
axes[0].set_title("Ważność cech wyznaczona metodą LASSO")
axes[0].set_xlabel("Nazwa cechy")
axes[0].set_ylabel("Wpływ")

axes[1].bar(x_train.columns.values, decision_tree_coef)
axes[1].grid()
axes[1].set_xticks(x_train.columns.values)
axes[1].set_xticklabels(x_train.columns.values, rotation = 90)
axes[1].set_title("Wpływ cech na model - Decision Tree")
axes[1].set_xlabel("Nazwa cechy")
axes[1].set_ylabel("Wpływ")

plt.show()

features_selected = x_train.columns[lasso_coef > THRESH]
features_ignored = x_train.columns[lasso_coef <= THRESH]
print(features_selected)

# Usunięcie zmiennych nieistotnych
x_train = x_train.drop(columns=features_ignored)
x_val = x_val.drop(columns=features_ignored)
x_test = x_test.drop(columns=features_ignored)

# Ponowne stworzenie pipeline'u oraz trenowanie modelu drzewa decyzyjnego dla zestawu z nowymi zmiennymi

col_categorical = x_train.select_dtypes(include='object').columns
col_numerical = x_train.select_dtypes(exclude='object').columns

col_transformer = make_column_transformer(
    (StandardScaler(), col_numerical),
    (OrdinalEncoder(), col_categorical)
)

decision_tree = Pipeline([
    ('col_transformer', col_transformer),
    ('decision_tree', DecisionTreeRegressor(max_depth=best_depth))
])


decision_tree.fit(x_train, y_train)

# Wyznaczenie wpłwu cech niezależnych na model

decision_tree_coef = np.abs(decision_tree['decision_tree'].feature_importances_)
decision_tree_coef /= np.sum(decision_tree_coef)

# plotting the Column Names and Importance of Columns.
fig,ax = plt.subplots(1,1,figsize=(5,3))

ax.bar(x_train.columns.values, decision_tree_coef)
ax.grid()
ax.set_xticks(x_train.columns.values)
ax.set_xticklabels(x_train.columns.values, rotation = 90)
ax.set_title("Wpływ cech na model - Decision Tree")
ax.set_xlabel("Nazwa cechy")
ax.set_ylabel("Wpływ")

plt.show()

# Ewaluacja na zestawie walidacyjnym
y_pred = decision_tree.predict(x_val)
print(f"RMSE: {mean_squared_error(y_val, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_val, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_val, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw walidacyjny")
ax.grid(True)
plt.show()

"""# Walidacja finalna"""

y_pred = decision_tree.predict(x_test)
print(f"RMSE: {mean_squared_error(y_test, y_pred)**.5:.2f}")
print(f"R^2: {r2_score(y_test, y_pred):.3f}")

fig, ax = plt.subplots(1,1,figsize=(5,5))

ax.plot(y_test, y_pred, '.')
ax.plot([0, np.max(y_val)], [0, np.max(y_val)], color='red', linestyle='--', linewidth=1)
ax.set_xlabel("Oczekiwane wartości")
ax.set_ylabel("Predykcje")
ax.set_title("Zestaw testowy")
ax.grid(True)
plt.show()