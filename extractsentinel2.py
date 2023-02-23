import fiona
import os
from shapely.geometry import shape
from sentinelhub import WmsRequest, CRS, BBox, DataCollection, SHConfig, MimeType
from sentinelhub.download import SentinelHubDownloadClient
from concurrent.futures import ThreadPoolExecutor

# Replace "" with the path to your shapefile
with fiona.open("C:/Users/pichaya/Gruming/pilot_1_westcoast/pilot_1_shp/Deepwater8_wgs84.shp", "r") as shp:
    # Get all features (polygons) from the shapefile
    polygons = [shape(feature["geometry"]) for feature in shp]

# Define the time range and image size
time_range = ('2020-01-01', '2020-12-31')
image_size = (512, 512)

# Set up the Sentinel Hub configuration
config = SHConfig()
config.instance_id = 'db4ee28e-5e65-45a0-967f-3fc8df4af884'
config.sh_client_id = '0a4e3cfc-c696-4130-a9f8-60a32e2afe0a'
config.sh_client_secret = 'f_M#B@.lbC7KVlDcM+25HNIOu]b6%A-Fi~5ff[G8'

# Set up the Sentinel Hub download client
download_client = SentinelHubDownloadClient(config=config)

# Define the folder path where the images will be saved
folder_path = 'C:/Users/pichaya/Gruming/data/'
max_threads = 5

# Loop over each polygon and download the images
for i, polygon in enumerate(polygons):
    # Define the coordinates of the bounding box
    min_lon, min_lat, max_lon, max_lat = polygon.bounds
    bbox = BBox(bbox=[min_lon, min_lat, max_lon, max_lat], crs=CRS.WGS84)

    # Define the Sentinel-2 image request
    request = WmsRequest(layer='TRUE-COLOR',
                         bbox=bbox,
                         time=time_range,
                         width=image_size[0],
                         height=image_size[1],
                         image_format= MimeType.TIFF,
                         data_collection=DataCollection.SENTINEL2_L1C,
                         config=config)

    # Download the images and save them to a file
    images = request.get_data()
    for j, image in enumerate(images):
        # Define the filename for the image
        filename = os.path.join(folder_path, f'image_{i}_{j}.tiff')
        
        # Download the image
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            download_client.download(image, filename)
