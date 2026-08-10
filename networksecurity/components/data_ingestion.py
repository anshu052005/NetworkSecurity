from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


## configuration of the Data Ingestion Config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pandas as pd
import pymongo
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")




class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            # self.data_ingestion_config = dataingestionconfig
            # aur ye dataingestionconfig main.py se aa rha hai
            # jaha se isne DataIngestionConfig ka object banaya tha aur usme TrainingPipelineConfig ka object pass kiya tha.
            # jisse usko database_name and collection_name mil gaye the.
            # fir yaha pe self.data_ingestion_config me store kar diya jisse hum is class ke andar kahi bhi use kar sakte hai.
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_collection_as_dataframe(self):
        """
        Read data from mongodb
        """
        try:

            # yaha pe humne database_name and collection_name ko self.data_ingestion_config se access kiya jisse hume database_name and collection_name mil gaya.
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name

            # yaha pe humne pymongo ka client banaya aur usme MONGO_DB_URL pass kiya jisse hum mongodb se connect ho gaye.
            # ek client ka matlab hai ki hum mongodb ke server se connect ho gaye aur ab hum usme database and collection ko access kar sakte hai.
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            # self.mongo_client["NetworkData"]["phishing_data"]
            #  ye humne database_name and collection_name ke through access kiya aur usko collection me store kar diya.
            
            collection=self.mongo_client[database_name][collection_name]




                    # MongoDB Collection
                    #         │
                    #         ▼
                    # collection.find()
                    #         │
                    #         ▼
                    # Cursor
                    #         │
                    #         ▼
                    # list(...)
                    #         │
                    #         ▼
                    # Python List
                    #         │
                    #         ▼
                    # pd.DataFrame(...)
                    #         │
                    #         ▼
                    # DataFrame
                    #         │
                    #         ▼
                    #        df
            # yaha pe humne collection.find() kiya jisse hume cursor mil gaya aur usko list me convert kiya aur fir usko pandas dataframe me convert kar diya
            # cursor ka matlab hai ki humne database me query kiya aur uska result hume mila. aur fir usko list me convert kiya jisse hume python list mil gaya. aur fir usko pandas dataframe me convert kiya jisse hume dataframe mil gaya.
            df=pd.DataFrame(list(collection.find()))

            # yaha pe humne check kiya ki agar dataframe me "_id" column hai to usko drop kar do. kyunki "_id" column mongodb ka unique identifier hota hai aur hume uski jarurat nahi hai.
            # mongodb ka ek rule hai ki har document me "_id" column hota hai jo unique hota hai. aur agar hum id nhi denge to wo khud bana dega. aur agar hum id denge to wo usko use karega. aur agar hum id ko drop kar denge to wo khud bana dega. isliye hume "_id" column ko drop karna chahiye.
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)

            # yaha pe humne check kiya ki agar dataframe me "na" value hai to usko np.nan me convert kar do. kyunki "na" value ka matlab hai ki wo value missing hai.
            # but numpy , pandas aur humara computer do not understand "na" value , so we replace it with NaN = Numpy Not a Number. kyunki numpy aur pandas ko NaN value samajh me aati hai aur wo usko handle kar sakte hai.
            df.replace({"na":np.nan},inplace=True) # inplace=True ka matlab hai ki humne dataframe me hi replace kar diya aur naya dataframe create nahi kiya. agar hum inplace=False karte to wo naya dataframe create karta aur hume usko store karna padta. but humne inplace=True kiya jisse humne dataframe me hi replace kar diya.

            #ye return df wapis initiate_data_ingestion() me jaayega jaha pe humne ye function call kiya tha. aur fir waha pe humne dataframe ko feature store me save kiya aur fir usko train test split kiya.
            return df

            # return df 
            #     │
            #     ▼
            # Wapas initiate_data_ingestion() me
        except Exception as e:
            raise NetworkSecurityException
            # MongoDB
            # ↓
            # Documents
            # ↓
            # DataFrame
            # ↓
            # _id Removed
            # ↓
            # "na"
            # ↓
            # NaN
        
    def export_data_into_feature_store(self,dataframe: pd.DataFrame):
        try:
            # yaha pe humne feature_store_file_path ko self.data_ingestion_config se access kiya jisse hume feature_store_file_path mil gaya. jisme humne dataframe ko save karna hai.
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            # Suppose : feature_store_file_path = artifacts/data_ingestion/feature_store/NetworkData.csv
            # neeche wale command se sirf : artifacts/data_ingestion/feature_store/ , matlab folder/directory tak ka path milega
            dir_path = os.path.dirname(feature_store_file_path)
            # os.makedirs(dir_path, exist_ok=True) ka matlab hai ki agar dir_path me folder/directory exist nahi karta hai to usko create kar do. aur agar exist karta hai to kuch mat karo. isliye humne exist_ok=True diya hai.
            os.makedirs(dir_path,exist_ok=True)
            # yaha pe humne dataframe as csv file banke  feature_store_file_path me save ho gayi. 
            # aur index=False ka matlab hai ki humne index ko save nahi kiya. 
            # aur header=True ka matlab hai ki humne header ko save kiya.
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe # dekho yaha pe humne csv file nhi balki dataframe hi return kiya hai kyuki hume aage train/test split krna hai aur hume dataframe hi chahiye hoga 
                             # ye jo csv file disk me save ki hai ye bss ek beech ka part tha , and hum aage bhi dataframe ko leke hi chalenge 
                                        # MongoDB
                                        #    │
                                        #    ▼
                                        # collection.find()
                                        #    │
                                        #    ▼
                                        # DataFrame
                                        #    │
                                        #    ▼
                                        # Remove MongoDB _id
                                        #    │
                                        #    ▼
                                        # "na" → NaN
                                        #    │
                                        #    ├──────────────► Feature Store CSV
                                        #    │
                                        #    ▼
                                        # Train/Test Split

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def split_data_as_train_test(self,dataframe: pd.DataFrame):
        try:
            # yaha pe hum basic train_test_split kr rahe hai
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio # yaha pe bhi humne jo test_size hai wo configuration se uthaya hai kyuki waha pe saare information available hai isi tarah ki
            )
            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of Data_Ingestion class"
            )

            
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            
            os.makedirs(dir_path, exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info(f"Exported train and test file path.")

            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
        
    def initiate_data_ingestion(self):
        try:
            # main.py
            #         │
            #         ▼
            # initiate_data_ingestion()
            #         │
            #         ▼
            # export_collection_as_dataframe()
            # yaha se humne data ko mongodb se read kiya aur dataframe me convert kiya
            dataframe=self.export_collection_as_dataframe()

            # MongoDB
            #       │
            #       ▼
            # DataFrame (RAM)
            #       │
            #       ▼
            # feature_store.csv (Disk)
            # Is project me Feature Store = CSV snapshot.
            dataframe=self.export_data_into_feature_store(dataframe)
            # neeche humne dataframe hi diya hai 
            self.split_data_as_train_test(dataframe)
                        #             MONGODB
                        #                │
                        #                ▼
                        #   export_collection_as_dataframe()
                        #                │
                        #                ▼
                        #          DataFrame
                        #                │
                        #          ┌─────┴─────┐
                        #          │           │
                        #       _id remove   "na" → NaN
                        #          │           │
                        #          └─────┬─────┘
                        #                ▼
                        #             DataFrame
                        #                │
                        #                ▼
                        #   export_data_into_feature_store()
                        #                │
                        #                ▼
                        #         Feature Store CSV
                        #                │
                        #                ▼
                        #    split_data_as_train_test()
                        #                │
                        #          ┌─────┴─────┐
                        #          ▼           ▼
                        #       train_set   test_set
                        #          │           │
                        #          ▼           ▼
                        #       train.csv    test.csv
            # yaha pe humne DataIngestionArtifact ka object banaya jisme humne training_file_path and testing_file_path pass kiya 
            #  jisme humne train.csv and test.csv save kiya tha.   
            # but hume yaha pe sirf path milega naki poora data kyuki artifacts me location kaha hai data ki wahi save hota hai actual data nhi save hota hai. aur ye artifact hume next step me use karna hai jaha pe hum data validation karenge.
            # 
            dataingestionartifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
                                                        test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifact # ye return hoke main.py me jayega

        except Exception as e:
            raise NetworkSecurityException