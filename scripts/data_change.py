import pandas as pd
from sklearn.preprocessing import MinMaxScaler, Normalizer, StandardScaler, LabelEncoder
from datetime import datetime
# When importing from notebook
import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))
from scripts.logger_creator import CreateLogger
import logging

class DataChange:
    def __init__(self, df: pd.DataFrame, deep=False):
        if(deep):
            self.df = df.copy(deep=True)
        else:
            self.df = df

    def optimize_df(self):
        data_types = self.df.dtypes
        optimizable = ['float64', 'int64']
        for col in data_types.index:
            if(data_types[col] in optimizable):
                if(data_types[col] == 'float64'):
                    # downcasting a float column
                    self.df[col] = pd.to_numeric(
                        self.df[col], downcast='float')
                elif(data_types[col] == 'int64'):
                    # downcasting an integer column
                    self.df[col] = pd.to_numeric(
                        self.df[col], downcast='unsigned')

        return self.df

    def get_min_max_of_dataframe_columns(self):
        top = self.df.max()
        top_df = pd.DataFrame(top, columns=['Max Value'])
        bottom = self.df.min()
        bottom_df = pd.DataFrame(bottom, columns=['Min Value'])
        info_df = pd.concat([top_df, bottom_df], axis=1)
        return info_df
    
    def standardize_columns(self, column) -> pd.DataFrame:
        try:        
            std_column_df = pd.DataFrame(self.df[column])
            std_column_values = std_column_df.values
            standardizer = StandardScaler()
            normalized_data = standardizer.fit_transform(std_column_values)
            self.df[column] = normalized_data
            logging.info('Successfull data scaling')
            return df
        except:
            logging.info('error in scaling data')
