#!/usr/bin/env python
# coding: utf-8


#imports and load the CSV
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import os
from datetime import datetime


#Make plots display bigger in the notebook
plt.rcParams['figure.figsize'] = (8,5)

#Load dataset
df = pd.read_csv("movies.csv")

#Showing the first few rows and basic info
print("First 5 rows:")
print(df.head())
print("\nInfo:")
print(df.info())
print("\nMissing values per column:")
print(df.isna().sum())

#remove duplicates and clean simple text issues
print("Initial shape:", df.shape)
#Remove exact duplicates
dupes = df.duplicated().sum()
print(f"Duplicates found: {dupes}")
df = df.drop_duplicates()
print("Shape after dropping duplicates:", df.shape)

#Clean newline characters and strip spaces in text columns
text_cols = ['MOVIES', 'GENRE', 'ONE-LINE', 'STARS']
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()

#Show a small sample after cleaning
print(df.head())


#extract year number (4-digit) from YEAR column
if 'YEAR' in df.columns:
    df['YEAR'] = df['YEAR'].astype(str).str.extract(r'(\d{4})')  # get 4-digit year
    df['YEAR'] = pd.to_numeric(df['YEAR'], errors='coerce')

print("YEAR column unique sample:")
print(df['YEAR'].dropna().unique()[:10])


#convert VOTES and Gross to numeric
if 'VOTES' in df.columns:
    df['VOTES'] = df['VOTES'].astype(str).str.replace(',', '', regex=True)
    df['VOTES'] = pd.to_numeric(df['VOTES'], errors='coerce')

if 'Gross' in df.columns:
    # Remove currency symbols and commas; if empty make 0
    df['Gross'] = df['Gross'].astype(str).str.replace('[^0-9.]', '', regex=True)
    df['Gross'] = pd.to_numeric(df['Gross'], errors='coerce').fillna(0)

print(df[['VOTES','Gross']].head())


#handle missing values: numeric columns -> median, categorical -> mode
numeric_cols = ['RATING', 'VOTES', 'RunTime', 'Gross']
for col in numeric_cols:
    if col in df.columns:
        med = df[col].median()
        df[col] = df[col].fillna(med)
        print(f"Filled missing {col} with median = {med}")

#For GENRE fill with mode if missing
if 'GENRE' in df.columns:
    mode_genre = df['GENRE'].mode()[0]
    df['GENRE'] = df['GENRE'].fillna(mode_genre)
    print("Filled missing GENRE with mode:", mode_genre)


#feature engineering: number of stars & number of genres
if 'STARS' in df.columns:
    df['num_stars'] = df['STARS'].apply(lambda x: len([s for s in str(x).split(',') if s.strip()]) )

if 'GENRE' in df.columns:
    df['num_genres'] = df['GENRE'].apply(lambda x: len([g for g in str(x).split(',') if g.strip()]) )

#show new features
print(df[['STARS','num_stars','GENRE','num_genres']].head())


#clip extreme RunTime values at 99th percentile
if 'RunTime' in df.columns:
    upper = df['RunTime'].quantile(0.99)
    print("99th percentile RunTime:", upper)
    # Clip values higher than this to the 99th percentile
    df.loc[df['RunTime'] > upper, 'RunTime'] = upper
    print("Applied clipping to RunTime.")


#scale numeric columns so models will behave better
scaler_cols = [c for c in ['RATING','VOTES','RunTime','Gross'] if c in df.columns]
if scaler_cols:
    scaler = MinMaxScaler()
    df[scaler_cols] = scaler.fit_transform(df[scaler_cols])
    print("Scaled columns:", scaler_cols)
    print(df[scaler_cols].describe().T)


#final checks and save cleaned file
print("Final shape:", df.shape)
print("Missing values after cleaning:")
print(df.isna().sum())

#Save cleaned CSV
df.to_csv("cleaned_files/movies_cleaned.csv", index=False)
print("Saved cleaned dataset as movies_cleaned.csv in cleaned_files folder.")

#putting date and time with each file
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join("cleaned_files", f"movies_cleaned_{timestamp}.csv")
df.to_csv(output_path, index=False)



#visualizations
# Missing values heatmap (after cleaning)
sns.heatmap(df.isna(), cbar=False)
plt.title("Missing Values After Cleaning")
plt.show()

#Rating distribution
if 'RATING' in df.columns:
    sns.histplot(df['RATING'], bins=20)
    plt.title("Rating Distribution (scaled)")
    plt.show()

#RunTime boxplot
if 'RunTime' in df.columns:
    sns.boxplot(x=df['RunTime'])
    plt.title("RunTime (after clipping)")
    plt.show()

#Show a small sample of cleaned data
print(df.head(10))
