import pandas as pd
import numpy as np
import requests
import json
import os

FOLDER_NAME = "NEPAL_FLOOD_DATA" # optional ! name of the folder can be changed and json data will be saved in it.
# Below links were obtained from "https://data.humdata.org/dataset/hot_flood_npl" 

links = {
    "Area of Interest" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/combined/hot_flood_npl_aoi.geojson",
    "Bridge Damage Assessment" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL/combined/hot_flood_npl_bridge_damage.geojson",
    "Bridges Info" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/bridges/hot_flood_npl_bridges_osm.geojson",
    "Destroyed & Damaged Features" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/destroyed_features/hot_flood_npl_destroyed_features_osm.geojson",
    "Education Facilities" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/education_facilities/hot_flood_npl_education_facilities_osm.geojson",
    "Exposed Hydropower" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL/combined/hot_flood_npl_exposed_hydropowers.geojson",
    "Financial Services" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/financial_services/hot_flood_npl_financial_services_osm.geojson",
    "Flood Extent (Observed August 2027)": "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL/combined/hot_flood_npl_flood_extent.geojson",
    "Health Facilities" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/health_facilities/hot_flood_npl_health_facilities_osm.geojson",
    "Helipads":"https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/helipads/hot_flood_npl_helipads_osm.geojson",
    "Layer Meta Data" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/combined/hot_flood_npl_osm_metadata.json",
    "Layer Meta Data (Overture)" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL/combined/hot_flood_npl_overture_metadata.json",
    "Mapping Task Boundaries" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL/tasking_manager/hot_flood_npl_tm_projects.geojson",
    "Open Spaces" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/open_spaces/hot_flood_npl_open_spaces_osm.geojson",
    "POI's" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/points_of_interest/hot_flood_npl_points_of_interest_osm.geojson",
    "Police Stations" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/police_stations/hot_flood_npl_police_stations_osm.geojson",
    "Residential Areas" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/residential_areas/hot_flood_npl_residential_areas_osm.geojson",
    "Settlement Names" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/populated_places/hot_flood_npl_populated_places_osm.geojson",
    "Waterways" : "https://production-raw-data-api.s3.amazonaws.com/ISO3/NPL_FLOOD/waterways/hot_flood_npl_waterways_osm.geojson",
}

# get function which shall be used to check status code by sending request to each link in the link dictionary 

def get_link_status(link):
    try:
        res = requests.get(link)
        
        if res.status_code == 200:
            print("Success from site data status code!")
            return res.json() # to parse json files
        
        else:
            print(f"Request failed with status code : {res.status_code}")

    except Exception as e:
        print(f"Unexpected Error : {e}")
        
# get function to send request to each link available in the link dictionary , giving them appropriate file names and... 
#... eventually save them in the FOLDER_NAME for better management of the files

def get_files(filename):
        
    try:
        for name,link in filename.items():
            
            #download the data
            raw_data = get_link_status(link)
            
            #Creates filename from dictionary keys
            filename = name.replace(" ","_")
            
            #save the json files in FOLDER_NAME
            
            file_path = os.path.join(FOLDER_NAME,f"{filename}.json")
            
            with open(f"{file_path}","w") as f:
                json.dump(raw_data,f,indent=4)
                
            print(f"Successfully saved : {filename}.json ")

    except Exception as e:
        print(f"Unexpected Error : {e}")    
        
try:
    files = get_files(links) # calling get file function
    
except Exception as e:
    print(f"Unexpected Error occurred while saving {e}")
    
def get_all_file(): # getting all files in the original json folder 
    
    all_files = []
    
    try:
        for i in range(len(links)):
            dir_filename = f"{list(links.keys())[i].replace(' ', '_')}.json"
            doc = f"{FOLDER_NAME}/{dir_filename}"
            all_files.append(doc)
        return all_files    
            
    except Exception as e:
        print(f"Failed to get file : {e}")

files = get_all_file()

def data_transforming_pipeline(files):
    
    clean_folder_path = "C:/Users/Aamir Bin Abbas/Desktop/Research & Thesis/Nepal Disaster/CLEAN_NEPAL_FLOOD_DATA"
    
    try:
        os.makedirs(clean_folder_path,exist_ok=True)
            
        rows = []
    
        for doc in files:
            try:
                
                #load json data
                with open(doc,'r',encoding='utf-8') as f:
                    data = json.load(f)
                    
                # skip files without geographical data
                if not isinstance(data.get("features"),list):
                    print(f'Skipped file : {doc}')
                    continue
                
                rows = []
                
                
                # extract properties and geometry from each feature
                for feature  in data['features']:
                    
                    geometry =  feature.get("geometry") or {}
                    
                    row = {
                        **(feature.get("properties") or {}),
                        "geometry_type": geometry.get("type"),
                        "coordinates": geometry.get("coordinates")
                    }
                    rows.append(row)
                    
                #convert extracted records to dataframe
                df = pd.DataFrame(rows)
                    
                #convert a CSV filename based on json filename
                base_name = os.path.splitext(os.path.basename(doc))[0]
                clean_file_name = f"cleaned_{base_name}.csv"
                    
                #constructing the complete output path
                full_clean_path = os.path.join(clean_folder_path,clean_file_name)
                    
                # saving dataframe as CSV 
                df.to_csv(full_clean_path,index=False,encoding="utf-8")
                    
                print(f"Saved: {clean_file_name} | Rows: {len(df)}")
                    
            except Exception as e:
                print(f"Failed to process {doc}: {e}")
                continue
        
        
    except Exception as e:
        print(f"Failed to prepare output folder: {e}")  

all_clean_files = data_transforming_pipeline(files)