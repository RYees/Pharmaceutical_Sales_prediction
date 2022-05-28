import pandas as pd
from sklearn.preprocessing import MinMaxScaler, Normalizer, StandardScaler, LabelEncoder
from datetime import datetime
# When importing from notebook
import sys
import os
sys.path.append(os.path.abspath(os.path.join('..')))
from scripts.logger_creator import CreateLogger
logger = CreateLogger('Data Manipulatior', handlers=1)
logger = logger.get_default_logger()
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
            # logging.info('Successfull data scaling')
            return self.df
        except:
            logging.info('error in scaling data')

    def add_week_day(self, day_of_week_col: str) -> pd.DataFrame:
        try:
            date_index = self.df.columns.get_loc(day_of_week_col)
            self.df.insert(date_index + 1, 'WeekDay',
                           self.df[day_of_week_col].apply(lambda x: 1 if x <= 5 else 0))

            logger.info("Successfully Added WeekDay Column to the DataFrame")

        except Exception as e:
            logger.exception("Failed to Add WeekDay Column")
    

    def affect_list(self, change_list, interval, duration, index):
        start_pt = int(index-duration/2) - interval
        try:
            for index in range(start_pt, start_pt + interval):
                change_list[index] = 'before'
            for index in range(start_pt + interval, start_pt + interval + duration):
                change_list[index] = 'during'
            for index in range(start_pt + interval + duration, start_pt + interval + duration + interval):
                change_list[index] = 'after'
        except:
            pass

        return change_list

    def modify_holiday_list(self, holiday_list: list) -> list:
        new_index = ["neither"] * len(holiday_list)
        for index, value in enumerate(holiday_list):
            if value == 'a':  # public holiday
                self.affect_list(new_index, 3, 1, index)
            elif value == 'b':  # Easter
                self.affect_list(new_index, 10, 50, index)
            elif value == 'c':  # christmas
                self.affect_list(new_index, 5, 12, index)
            else:
                pass

        return new_index


    def add_number_of_days_to_holiday(self, state_holiday_col: str):
        try:
            date_index = self.df.columns.get_loc(state_holiday_col)

            modified_index = self.modify_holiday_list(
                self.df[state_holiday_col].values.tolist())
            days_to_holiday_index = []
            i = 0
            last_holiday_index = 0
            for index, value in enumerate(modified_index):
                if(index == len(modified_index) - 1):
                    for j in range(last_holiday_index+1, len(modified_index)):
                        days_to_holiday_index.append(0)
                elif(value == 'neither' or value == 'after' or value == 'before'):
                    i += 1
                elif(value == 'during' and i != 0):
                    last_holiday_index = index
                    for j in range(i):
                        days_to_holiday_index.append(i)
                        i = i-1
                    days_to_holiday_index.append(0)
                    i = 0
                elif(value == 'during' and i == 0):
                    days_to_holiday_index.append(i)
                    last_holiday_index = index
                    continue

            self.df.insert(date_index + 1, 'DaysToHoliday',
                           days_to_holiday_index)

            logger.info("Successfully Added DaysToHoliday Column")

        except Exception as e:
            logger.exception("Failed to Add DaysToHoliday Column")

    def return_day_status_in_month(self, day: int) -> int:
        # conside 1 is beginning of month, 2 is middle of the month and 3 is end of the month
        if(day <= 10):
            return 1
        elif(day > 10 and day <= 20):
            return 2
        else:
            return 3
            
    def add_number_of_days_after_holiday(self, state_holiday_col: str):
        try:
            date_index = self.df.columns.get_loc(state_holiday_col)

            modified_index = self.modify_holiday_list(
                self.df[state_holiday_col].values.tolist())

            days_to_after_holiday_index = [0] * len(modified_index)
            i = 0
            last_holiday_index = modified_index.index('during')

            for index, value in enumerate(modified_index):
                if(value == 'before'):
                    if(index > last_holiday_index):
                        i += 1
                        days_to_after_holiday_index[index] = i
                    continue
                elif(value == 'after'):
                    i += 1
                    days_to_after_holiday_index[index] = i
                elif(value == 'during'):
                    last_holiday_index = index
                    i = 0
                    continue

            days_to_after_holiday_index.insert(0, 0)

            self.df.insert(date_index + 1, 'DaysAfterHoliday',
                           days_to_after_holiday_index[:-1])

            logger.info("Successfully Added DaysAfterHoliday Column")

        except Exception as e:
            logger.exception("Failed to Add DaysAfterHoliday Column")

    
    def add_month_timing(self, day_col: str) -> pd.DataFrame:
        try:
            date_index = self.df.columns.get_loc(day_col)
            self.df.insert(date_index + 1, 'MonthTiming',
                           self.df[day_col].apply(self.return_day_status_in_month))

            logger.info("Successfully Added MonthTiming Column")

        except Exception as e:
            logger.exception("Failed to Add MonthTiming Column")