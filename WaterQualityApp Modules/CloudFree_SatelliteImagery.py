## -*- coding: utf-8 -*-
"""
Created on Sat Apr 8 14:13:00 2023
    By Saeed Rahimi
    V 1.0 Date 08/04/2023
    This madual includes several functions for downlaoding the satelite imageries from Google Earth Engine:
        Search for the imagery during the specified time-period
        Detects and removes the clouds in the scene
        Takes the median value of each pixel in all images in the stack (for the specified time-period)
        Creates a composite image       
    @author: sarsh
"""
import sys
import subprocess

try:
    import ee
    print('The required modules are installed')
except ModuleNotFoundError:
    print('The required modules are NOT installed')

    # 👇️ optionally install module
    python = sys.executable
    subprocess.check_call(
        [[python, '-m', 'pip', 'install', 'google-api-python-client'],
        [python, '-m', 'pip', 'install', 'earthengine-api']],
        stdout=subprocess.DEVNULL
    )
finally:
    import ee
    
service_account = 'water-quality-app@waterqualityapp-383404.iam.gserviceaccount.com'
authentication_file = 'WaterQualityApp_PrivateKey.json'
credentials = ee.ServiceAccountCredentials(service_account, authentication_file)
ee.Initialize()

# Get a cloud free Sentinal2 composite from a colection between the START_DATE and END_DATE
def cld_free_sl2(START_DATE, END_DATE, CONFIGURATION, AOI):   
## %% Build a Sentinel-2 collection
    ## Define build a Sentinel-2 collection function
    def get_s2_sr_cld_col(start_date, end_date, aoi):
        ## Import and filter S2 SR.
        s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR')
            .filterBounds(aoi)
            ## .filter(ee.Filter.calendarRange(START_YEAR,END_YEAR,'year'))
            ## .filter(ee.Filter.calendarRange(START_MONTH,END_MONTH,'month'))
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER)))
     
        ## Import and filter s2cloudless.
        s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
            .filterBounds(aoi)
            ## .filter(ee.Filter.calendarRange(START_YEAR,END_YEAR,'year'))
            ## .filter(ee.Filter.calendarRange(START_MONTH,END_MONTH,'month'))
            .filterDate(start_date, end_date))
     
     
        ## Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
        return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
            'primary': s2_sr_col,
            'secondary': s2_cloudless_col,
            'condition': ee.Filter.equals(**{
                'leftField': 'system:index',
                'rightField': 'system:index'
            })
        }))

## %% Cloud components
    def add_cloud_bands(img):
        ## Get s2cloudless image, subset the probability band.
        cld_prb = ee.Image(img.get('s2cloudless')).select('probability')
    
        ## Condition s2cloudless by the probability threshold value.
        is_cloud = cld_prb.gt(CLD_PRB_THRESH).rename('clouds')
    
        ## Add the cloud probability layer and cloud mask as image bands.
        return img.addBands(ee.Image([cld_prb, is_cloud]))


## %% Cloud shadow components
    def add_shadow_bands(img):
        ## Identify water pixels from the SCL band.
        not_water = img.select('SCL').neq(6)
    
        ## Identify dark NIR pixels that are not water (potential cloud shadow pixels).
        SR_BAND_SCALE = 1e4
        dark_pixels = img.select('B8').lt(NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')
    
        ## Determine the direction to project cloud shadow from clouds (assumes UTM projection).
        shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));
    
        ## Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
        cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, CLD_PRJ_DIST*10)
            .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
            .select('distance')
            .mask()
            .rename('cloud_transform'))
    
        ## Identify the intersection of dark pixels with cloud shadow projection.
        shadows = cld_proj.multiply(dark_pixels).rename('shadows')
    
        ## Add dark pixels, cloud projection, and identified shadows as image bands.
        return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))


    ## %% Final cloud-shadow mask
    def add_cld_shdw_mask(img):
        ## Add cloud component bands.
        img_cloud = add_cloud_bands(img)
    
        ## Add cloud shadow component bands.
        img_cloud_shadow = add_shadow_bands(img_cloud)
    
        ## Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
        is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)
    
        ## Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
        ## 20 m scale is for speed, and assumes clouds don't require 10 m precision.
        is_cld_shdw = (is_cld_shdw.focal_min(2).focal_max(BUFFER*2/20)
            .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
            .rename('cloudmask'))
    
        ## Add the final cloud-shadow mask to the image.
        return img.addBands(is_cld_shdw)

    ## %% Define cloud mask application function
    def apply_cld_shdw_mask(img):
        ## Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
        not_cld_shdw = img.select('cloudmask').Not()
    
        ## Subset reflectance bands and update their masks, return the result.
        return img.select('B.*').updateMask(not_cld_shdw)
    
    ## Configure the cloud details
    CLOUD_FILTER = CONFIGURATION['CLOUD_FILTER']
    CLD_PRB_THRESH = CONFIGURATION['CLD_PRB_THRESH']
    NIR_DRK_THRESH = CONFIGURATION['NIR_DRK_THRESH']
    CLD_PRJ_DIST = CONFIGURATION['CLD_PRJ_DIST']
    BUFFER = CONFIGURATION['BUFFER']
    
    ## %% Return the cloud free single image
    s2_sr_cld_col = get_s2_sr_cld_col(START_DATE, END_DATE, AOI)
    s2_sr_cldless = (s2_sr_cld_col.filterBounds(AOI)
                                  .map(add_cld_shdw_mask)
                                  .map(apply_cld_shdw_mask)
                                  .median())
    return s2_sr_cldless


# Get a cloud free Landsat8 composite from a colection between the START_DATE and END_DATE
def cld_free_ls(START_DATE, END_DATE, CONFIGURATION, AOI):
    ## Parse a string to an integer
    def parseInt(s):
        digits = ''
        for c in str(s).strip():
            if not c.isdigit():
                break
            digits += c
        return int(digits) if digits else None

    ## Scale and mask Landsat 8 (C2) surface reflectance images.
    def prep_sr_L8(image):
        ## Develop masks for unwanted pixels (fill, cloud, cloud shadow).
        qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111')).eq(0)
        saturationMask = image.select('QA_RADSAT').eq(0)

        ## Apply the scaling factors to the appropriate bands.
        def get_factor_img(factor_names):
            factor_list = image.toDictionary().select(factor_names).values()
            return ee.Image.constant(factor_list)

        scaleImg = get_factor_img(['REFLECTANCE_MULT_BAND_.|TEMPERATURE_MULT_BAND_ST_B10'])
        offsetImg = get_factor_img(['REFLECTANCE_ADD_BAND_.|TEMPERATURE_ADD_BAND_ST_B10'])
        scaled = image.select('SR_B.|ST_B10').multiply(scaleImg).add(offsetImg)

        ## Replace original bands with scaled bands and apply masks.
        return image.addBands(scaled, None, True).updateMask(qaMask).updateMask(saturationMask)

    ## Landsat 8 Collection 2 surface reflectance images of interest.
    ls_sr_cldless = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')\
                        .filterBounds(AOI).filterDate(START_DATE, END_DATE)\
                        .map(prep_sr_L8)\
                        .select('SR.*')\
                        .median()
     
    return ls_sr_cldless


## Get a cloud free MODIS composite from a colection between the START_DATE and END_DATE
def cld_free_mo(START_DATE, END_DATE, CONFIGURATION, AOI):
    import math
    ## helper function to extract the QA bits
    def get_QA_bits(image, s_bit, e_bit, new_name):
        ## Compute the bits we need to extract.
        pattern = 0
        for i in range(s_bit, e_bit, 1):
            pattern += math.pow(2, i)

        ## Return a single band image of the extracted QA bits, giving the band a new name.
        return image.select([0], [new_name]) \
                      .bitwiseAnd(pattern) \
                      .rightShift(s_bit)

    ## A function to mask out cloudy pixels.
    def mask_quality(image):
        ## Select the QA band.
        QA = image.select('StateQA')
        ## Get the internal_cloud_algorithm_flag bit.
        internal_quality = get_QA_bits(QA, 8, 13, 'internal_quality_flag')
        ## Return an image masking out cloudy areas.
        return image.updateMask(internal_quality.eq(0))


    ## Get the collection
    collection = ee.ImageCollection('MODIS/MOD09A1')

    ## Define a list of bands
    modis_bands = ['sur_refl_b03','sur_refl_b04','sur_refl_b01','sur_refl_b02','sur_refl_b06','sur_refl_b07']
    ls_bands = ['blue','green','red','nir','swir1','swir2']

    ## create cloud free composite
    mo_sr_cldless = collection.filterDate(ee.Date(START_DATE), \
                                          ee.Date(END_DATE)) \
                                .filterBounds(AOI) \
                                .map(mask_quality) \
                                .select(modis_bands, ls_bands) \
                                .median()
    
    return mo_sr_cldless