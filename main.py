from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig

from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import ModelTrainerConfig
 

import sys

if __name__=='__main__':
    try:
        # config is like a blueprint of the project. It contains all the information about the project like where to store the artifacts, what is the name of the database, what is the name of the collection, what is the train test split ratio, etc.
        # components are the actual implementation of the project. It contains all the logic of the project like how to read data from mongodb, how to split data into train and test, how to validate data, how to transform data, how to train model, etc.

        # step 1 : yaha pe humne TrainingPipelineConfig ka object banaya jisse hume artifact_dir mil gaya jisme humne timestamp ke sath artifact create kiya tha.
        # step 2 : fir humne DataIngestionConfig ka object banaya jisme humne TrainingPipelineConfig ka object pass kiya jisse hume database_name and collection_name mil gaya.
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
        # step 3 : fir humne DataIngestion ka object banaya jisme humne DataIngestionConfig ka object pass kiya jisse hume database_name and collection_name mil gaya.
        data_ingestion=DataIngestion(dataingestionconfig)
        # step 4 : fir humne initiate_data_ingestion() method call kiya jisse humne data ko mongodb se read kiya aur dataframe me convert kiya aur fir usko feature store me save kiya aur fir usko train test split kiya.
        logging.info("Initiate the data ingestion")
        # ye function hume DataIngestionArtifact return karega jisme hume feature_store_file_path, training_file_path, testing_file_path mil jayega. and this method is better because it will return the artifact which we can use in the next step.
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
                    # python main.py
                    #         │
                    #         ▼
                    # TrainingPipelineConfig()
                    #         │
                    #         ▼
                    # DataIngestionConfig()
                    #         │
                    #         ▼
                    # DataIngestion()          ← Object created
                    #         │
                    #         ▼
                    # logging.info()           ← Log written
                    #         │
                    #         ▼
                    # initiate_data_ingestion()  ← FIRST REAL WORK STARTS , Ab hum pehli baar main.py se bahar niklenge.      
        logging.info("Data Initiation Completed")
                    # main.py
                    #    │
                    #    ▼
                    # DataIngestionConfig
                    #    │
                    #    ▼
                    # DataIngestion
                    #    │
                    #    ▼
                    # initiate_data_ingestion()
                    #    │
                    #    ▼
                    # MongoDB
                    #    │
                    #    ▼
                    # collection.find()
                    #    │
                    #    ▼
                    # DataFrame
                    #    │
                    #    ▼
                    # Basic cleaning(_id , "na")
                    #    │
                    #    ▼
                    # Feature Store CSV
                    #    │
                    #    ▼
                    # Train/Test Split
                    #    │
                    #    ├──────────► train.csv
                    #    │
                    #    └──────────► test.csv
                    #                  │
                    #                  ▼
                    #         DataIngestionArtifact
                    #                  │
                    #                  ▼
                    #               main.py
        print(dataingestionartifact)

        # Data Ingestion
        #        │
        #        │ creates
        #        ▼
        # DataIngestionArtifact
        #        │
        #        │ passed into
        #        ▼
        # DataValidation
        data_validation_config=DataValidationConfig(trainingpipelineconfig)
        data_validation=DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Initiate the data Validation")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("data Validation Completed")
        print(data_validation_artifact)
        data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
        logging.info("data Transformation started")
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("data Transformation completed")

        logging.info("Model Training sstared")
        model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact=model_trainer.initiate_model_trainer()
        
        logging.info("Model Training artifact created")
        
        
        
    except Exception as e:
           raise NetworkSecurityException(e,sys)


