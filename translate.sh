ten_m_filename='SENTINEL2_L1C:L1C_T41WMN_A017750_20200730T074614/S2B_MSIL1C_20200730T074619_N0209_R135_T41WMN_20200730T090552.SAFE/MTD_MSIL1C.xml:10m:EPSG_32641'
geotiff_args='-co TILED=YES'

gdal_translate "${ten_m_filename}" tile_2.jp2 -b 1
gdal_translate "${ten_m_filename}" tile_3.jp2 -b 2
gdal_translate "${ten_m_filename}" tile_4.jp2 -b 3
gdal_translate "${ten_m_filename}" tile_8.jp2 -b 4
gdal_translate "${ten_m_filename}" tile_2348.jp2 -b 1 -b 2 -b 3 -b 4

gdal_translate "${ten_m_filename}" -co TILED=YES tile_2.tif -b 1
gdal_translate "${ten_m_filename}" -co TILED=YES tile_3.tif -b 2
gdal_translate "${ten_m_filename}" -co TILED=YES tile_4.tif -b 3
gdal_translate "${ten_m_filename}" -co TILED=YES tile_8.tif -b 4
gdal_translate "${ten_m_filename}" -co TILED=YES tile_2348.tif -b 1 -b 2 -b 3 -b 4

gdal_translate "${ten_m_filename}" tile_2_non_cogeo.tif -b 1
gdal_translate "${ten_m_filename}" tile_3_non_cogeo.tif -b 2
gdal_translate "${ten_m_filename}" tile_4_non_cogeo.tif -b 3
gdal_translate "${ten_m_filename}" tile_8_non_cogeo.tif -b 4
gdal_translate "${ten_m_filename}" tile_2348_non_cogeo.tif -b 1 -b 2 -b 3 -b 4
