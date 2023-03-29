
import ee
ee.Authenticate()
ee.Initialize()

# Define the path to the shapefile on your local machine
path_to_shapefile = 'C:/Users/pichaya/Gruming/pilot_1_westcoast/pilot_1_shp/Deepwater8_wgs84.shp'

# Load the shapefile as an Earth Engine FeatureCollection
shapefile = ee.FeatureCollection('users/PichayaMelody123')

# Get the geometry of the shapefile
geometry = shapefile.geometry()

# Alternatively, you can also define the geometry by reading the shapefile from your local machine:
# shapefile = ee.FeatureCollection('shapefile/path', 'EPSG:4326')
# geometry = shapefile.geometry()

# Print the geometry to verify that it has been correctly assigned
print(geometry)

# Define the region of interest (ROI)
geometry = ee.Geometry.Point(-122.13, 37.44)

# Import the Sentinel-1 and Sentinel-2 data
sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD') \
    .filterDate('2019-01-01', '2019-12-31') \
    .filterBounds(geometry)
    
sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterDate('2019-01-01', '2019-12-31') \
    .filterBounds(geometry)

# Select the polarization and bands of the Sentinel-1 and Sentinel-2 images
vh = sentinel1.select('VH')
red = sentinel2.select('B4')
green = sentinel2.select('B3')
blue = sentinel2.select('B2')

# Define a function to convert Sentinel-1 VH polarization to optical values
def to_optical(image):
    optValue = image.expression(
        '(10**(vh/10.0))/2.0',
        {
            'vh': image.select('VH')
        }
    )
    return optValue.copyProperties(image, ['system:time_start'])

# Apply the toOptical function to the Sentinel-1 VH polarization and merge it with the Sentinel-2 data
optVH = sentinel1.map(to_optical)
optical = optVH.mosaic().addBands(red).addBands(green).addBands(blue)

# Define a function to apply a cloud mask to the optical image
def cloud_mask(image):
    qa = image.select('QA60')
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
        .And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask)

# Apply the cloud mask to the optical image
cloudFree = optical.map(cloud_mask)

# Visualize the cloud-free image
Map.addLayer(cloudFree, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}, 'Sentinel-2 Cloud-Free')