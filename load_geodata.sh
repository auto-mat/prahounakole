#!/bin/bash

: '
Get gdal-vfr cmd tool
http://freegis.fsv.cvut.cz/gwiki/RUIAN_/_GDAL#VFR_konverzn.C3.AD_skripty
http://freegis.fsv.cvut.cz/gwiki/RUIAN#P.C5.99ehled_poskytovan.C3.BDch_VFR_soubor.C5.AF
'

CZ_REGIONS_EPSG_4326=$1
CZ_REGIONS_EPSG_5514="cz_regions.db"

git clone https://github.com/ctu-geoforall-lab/gdal-vfr.git
cd gdal-vfr/
# Download Vusc (Czechia regions) layer
./vfr2ogr --type ST_UKSH --format "SQLite" --layer Vusc --geom OriginalniHranice --dsn "$('pwd')/data/${CZ_REGIONS_EPSG_5514}" --overwrite
cd data/
# Coordinate system conversion EPSG 5514 (S-JTSK) -> EPSG 5326
ogr2ogr -t_srs EPSG:4326 -f SQLite "${CZ_REGIONS_EPSG_4326}" "${CZ_REGIONS_EPSG_5514}"
