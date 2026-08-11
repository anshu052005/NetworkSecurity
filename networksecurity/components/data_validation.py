from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging 
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd
import os,sys
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            # Ab Data Validation ke paas 3 cheezein hain
            #                  DataValidation
            #                       │
            #         ┌─────────────┼──────────────┐
            #         ▼             ▼              ▼
            #    Artifact         Config        Schema
            #         │             │              │
            #         ▼             ▼              ▼
            #  train/test       output paths    expected
            #     paths                         structure

            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    # ye staticmethod ko koi bhi DataValidation class ka object chahiye hi nhi , 
    # dekho isme self hai hi nhi , isliye humne isko DataValidation() krke likha naki self. karke
                # Isko:

                # _schema_config nahi chahiye
                # data_ingestion_artifact nahi chahiye
                # data_validation_config nahi chahiye
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            # yaha se humne test and train file path ko read kiya aur csv file bana diya aur usko dataframe me convert kiya aur return kar diya
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

       
    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns=len(self._schema_config) # schema ke hisaab se column ki len nikaali
            logging.info(f"Required number of columns:{number_of_columns}")
            logging.info(f"Data frame has columns:{len(dataframe.columns)}")
            if len(dataframe.columns)==number_of_columns: # check kiya ki dataframe me required number of columns hai ya nhi
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    #  Is function ka main kaam ye check karna hai ki aapke Train Data (base_df) aur Test/New Data (current_df) ke beech mein koi bada badlaav (statistical change) toh nahi aaya hai.
    #  Is badlaav ko hi Machine Learning mein "Data Drift" kehte hain. 
    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            # shuru me hum maanke chalenge ki data drift nahi hua hai, isliye status ko True set karenge. Agar humko data drift milta hai toh hum status ko False kar denge.
            status=True
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]

                # Yahan Kolmogorov-Smirnov Test (ks_2samp) naam ka ek statistical function use ho raha hai (jo usually scipy.stats library se aata hai).
                # Ye test d1 aur d2 ko compare karta hai aur batata hai ki kya dono ka data distribution (pattern) same hai ya nahi.
                # Result mein ye ek p-value deta hai.
                is_same_dist=ks_2samp(d1,d2)

                # Agar p-value threshold se badi hai, iska matlab hai ki dono distributions same hain

                if threshold<=is_same_dist.pvalue:
                    is_found=False
                # Agar p-value threshold se chhoti ya barabar hai, iska matlab hai ki dono distributions alag hain (data drift hua hai).aur status bhi False ho jaayega.
                else:
                    is_found=True
                    status=False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                    
                    }})
            # upar  banayi gyi hui report ko hume kaha store krna hai uska path hume data_validation_config se mil jaayega.
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            #Create directory , upar jo humne report banayi hai usko hume store bhi krna hai as yaml file
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            # jaise pehle humne pd.read_csv() se dataframe ko read kiya tha aur fir usko csv file me save kiya tha, waise hi humne upar report banayi hai usko yaml file me save kar diya.
            write_yaml_file(file_path=drift_report_file_path,content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            # yaha se humne data validation ke liye train and test file path ko read kiya aur dataframe me convert kiya. fir humne number of columns validate kiya aur datadrift check kiya. finally humne DataValidationArtifact ka object banaya jisme humne validation_status, valid_train_file_path, valid_test_file_path, invalid_train_file_path, invalid_test_file_path, drift_report_file_path pass kiya.
                        # DataIngestionArtifact
                        #         │
                        #         ▼
                        # train.csv + test.csv
                        #         │
                        #         ▼
                        # DataValidation.read_data()
                        #         │
                        #         ▼
                        # train_dataframe + test_dataframe

            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            ## read the data from train and test
            # isko humne read_data() method me pass kiya jisko sirf file path chahiye aur koi bhi DataValidation ka oject nhi chahiye 
            # isliye isko humne thoda alag tareeke se likha hai , self. krke nhi likha .
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)
            
            ## validate number of columns

            status=self.validate_number_of_columns(dataframe=train_dataframe) # yaha se hume status milega true and false me, ye batayega ki train dataframe me required number of columns hai ya nhi humare schema ke hisaab se 
            if not status:
                error_message=f"Train dataframe does not contain all columns.\n"
            status = self.validate_number_of_columns(dataframe=test_dataframe) # yaha pe bh same column check hai bool me
            if not status:
                error_message=f"Test dataframe does not contain all columns.\n"   

            ## lets check datadrift
            status=self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)

            # Jaise humne data ingestion me tran.csv aur test.csv banaya tha 
            # Waise hi DataValidation me bhi validated train.csv aur test.csv banayenge 
            # Aur inn sabka location artifact ko bata denge .
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True

            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            # Yaha pe humne DataValidationArtifact ka object banaya hai 
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact # aur hum at last artifact hi return kr rhe hai main.py me aur ye data transformation me jayega
        except Exception as e:
            raise NetworkSecurityException(e,sys)

        
                            # Har component:
                            # Input Artifact → Processing → Output Artifact
                            # ┌─────────────────────┐
                            # │ Data Ingestion      │
                            # └─────────┬───────────┘
                            #           │
                            #           ▼
                            # DataIngestionArtifact
                            #           │
                            #           ▼
                            # ┌─────────────────────┐
                            # │ Data Validation     │
                            # └─────────┬───────────┘
                            #           │
                            #           ▼
                            # DataValidationArtifact
                            #           │
                            #           ▼
                            # ┌─────────────────────┐
                            # │ Data Transformation │
                            # └─────────────────────┘



