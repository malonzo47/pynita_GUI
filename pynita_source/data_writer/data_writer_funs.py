from osgeo import gdal
import os

#%%
def saveMI(MI_2d, prj, geotransform, path, fn):
    
    full_fn = os.path.join(path, fn)
    
    (x,y) = MI_2d.shape
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    dst_datatype = gdal.GDT_Byte
    dst_ds = driver.Create(full_fn, y, x, 1, dst_datatype)
    dst_ds.GetRasterBand(1).WriteArray(MI_2d)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(prj)
    