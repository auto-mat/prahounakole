#!/bin/bash

: '
Get gdal-vfr cmd tool
http://freegis.fsv.cvut.cz/gwiki/RUIAN_/_GDAL#VFR_konverzn.C3.AD_skripty
http://freegis.fsv.cvut.cz/gwiki/RUIAN#P.C5.99ehled_poskytovan.C3.BDch_VFR_soubor.C5.AF
'

LAYER=$1
OUTPUT_GEODATA_EPSG_4326=$2
IFS="."
read -a STARR <<< "$OUTPUT_GEODATA_EPSG_4326"
OUTPUT_GEODATA_EPSG_5514="${STARR[0]}_EPSG_5514.db"
TEMP_DIR=$3

cd $TEMP_DIR
git clone https://github.com/ctu-geoforall-lab/gdal-vfr.git
cd gdal-vfr/
# Download Vusc (Czechia regions) layer
./vfr2ogr --type ST_UKSH --format SQLite --layer $LAYER --geom OriginalniHranice --dsn "$('pwd')/data/${OUTPUT_GEODATA_EPSG_5514}" --overwrite
cd data/
# Coordinate system conversion EPSG 5514 (S-JTSK) -> EPSG 4326 (WGS-84)
ogr2ogr -t_srs EPSG:4326 -f SQLite "${OUTPUT_GEODATA_EPSG_4326}" "${OUTPUT_GEODATA_EPSG_5514}"
