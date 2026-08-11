import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN
from networksecurity.constant.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    DataValidationArtifact
)
# yes
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging
from networksecurity.utils.main_utils.utils import save_numpy_array_data,save_object

class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            
            # [CRITICAL FIX]: Agar column names me duplicate names ya spaces hain, toh unhe clean karein
            df.columns = df.columns.str.strip()
            
            # Agar kisi galti se 'URLURL_Length' jaisa naam database me chala gaya hai, toh use rename karein
            rename_dict = {
                'URLURL_Length': 'URL_Length',
                'having_IPhaving_IP_Address': 'having_IP_Address',
                'popUpWindow': 'popUpWidnow'  # Model expected spelling match karne ke liye
            }
            df.rename(columns=rename_dict, inplace=True)
            
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def get_data_transformer_object(self) -> Pipeline:  # Fixed: changed 'cls' to 'self'
        """
        It initialises a KNNImputer object with the parameters specified in the training_pipeline.py file
        and returns a Pipeline object with the KNNImputer object as the first step.
        """
        logging.info("Entered get_data_transformer_object method of Transformation class")
        try:
            # KNNImputer roughly ye idea use karta hai:

            # "Is missing value wali row ke sabse similar neighboring rows ka data dekho aur unse missing value estimate karo."
            # Hum yaha pe NaN values ko unke nearest neighbors ke average se replace kar rahe hain. Ye approach tab kaam aati hai jab data me patterns hote hain aur missing values random nahi hoti.
           imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
           logging.info(f"Initialise KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
           # Ye ML preprocessing pipeline hai. Abhi pipeline me sirf one step hai
           # Hum aur bhi steps add kr sakte hai in future jaise scaling, encoding, etc.:
                            # Raw Training Data (X_train with NaNs)
                            #                │
                            #                ▼
                            # ┌──────────────────────────────┐
                            # │  Step 1: "imputer"           │HUMARA PROJECT ME SIRF YAHI PART HAI NEECHE WALA SCALER PART NHI
                            # │  - Learns neighbor patterns  │
                            # │  - Replaces NaNs with values │
                            # └──────────────┬───────────────┘
                            #                │  Input: Array with NO NaNs
                            #                ▼
                            # ┌──────────────────────────────┐
                            # │  Step 2: "scaler"            │
                            # │  - Learns mean & std dev     │ YE HUMARE CURRENT MODEL ME NHI HAI BUT YE JUST AS AN EXAMPLE 
                            # │  - Scales values (mean=0,    │ USE KIYA HAI KI HUM IMPUTER KE ALAWA BHI AUR CHEEZE USE KR SAKTE HAI
                            # │    std=1)                    │
                            # └──────────────┬───────────────┘
                            #                │
                            #                ▼
                            # Final Processed NumPy Array (No NaNs + Scaled)           
           processor: Pipeline = Pipeline([("imputer", imputer)])
           return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)

        
    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Entered initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation")
            # yaha pe humne read_data() method call kiya jisse humne valid_train_file_path aur valid_test_file_path ko read kiya aur dataframe me convert kiya.
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # yaha pe humne train_df aur test_df me se target column ko alag kiya aur fir usko replace kiya -1 ko 0 se.
            ## training dataframe
            input_feature_train_df = train_df.drop(columns=[TARGET_COLUMN], axis=1) # target column ko drop kr diya
            target_feature_train_df = train_df[TARGET_COLUMN] # target column ko alag se store kr liya
            target_feature_train_df = target_feature_train_df.replace(-1, 0) # target column me -1 ko 0 se replace kr diya

            # testing dataframe
            # same kaam test ke sath bhi kiya
            input_feature_test_df = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # ye preprocessor ek recipe jaisa hai , abhi data transformation apply nhi hua hai , bass processor tayar hua hai jo humne upar se return kiya
            # Abhi KNNImputer ne actual data transform nahi kiya hai..
            preprocessor = self.get_data_transformer_object()

            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)
             
            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_df)]

            # save numpy array data
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, array=test_arr)
            
            # Save preprocessor object
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)
            
            # Ensure the final_model directory exists before saving
            os.makedirs("final_model", exist_ok=True)
            save_object("final_model/preprocessor.pkl", preprocessor_object)

            # preparing artifacts
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)