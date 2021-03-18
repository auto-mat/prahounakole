#!/usr/bin/env bash

: '
Concatenate, reclassify Czechia accidents data (CSV files) and convert
them into SQLITE db (geospatial layer). Transform them from EPSG 5514
(S-JTSK) to the EPS 4326 (WGS-84).
'

TEMP_DIR=$1
export ACCIDENTS_CSV_FILE=$2
ACCIDENTS_SPATIALLITE=$3

COLS="datum;den;cas;nasledky;zavineni;vozidlo;x;y"
echo $COLS > $ACCIDENTS_CSV_FILE
ACCIDENTS_CSV_FILE_BASENAME=$(basename $ACCIDENTS_CSV_FILE .csv)
ACCIDENTS_VRT_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}.vrt"
# LAYER_COLS=$(echo $COLS | cut -d ";" -f1-6 | sed "s/;/, /g")
# SQL="SELECT ${LAYER_COLS}, MakePoint(CAST(x AS float),CAST(y AS float)) FROM $(basename ${ACCIDENTS_CSV_FILE} )"

# Columns descriptions https://www.policie.cz/soubor/polozky-formulare-hlavicky-souboru-xlsx.aspx
find "$TEMP_DIR" -type f -name '*.csv' ! -name "$(basename ${ACCIDENTS_CSV_FILE})" -exec bash -c '
FILTER=(08.csv,09.csv,10.csv,11.csv,12.csv,13.csv,CHODCI.csv)
for file do
    if [[ ! "${FILTER}" =~ "$(basename "${file}")" ]]; then
       awk -F ";" '"'"'
       BEGIN {OFS=";"}
      {

        # "cas" column
        if ($6 == "\"2560\"")
           $6=""
        else if (length($6) == 6)
           $6=substr($6, 2, 2)":"substr($6, 4, 2)
        else
           $6=substr($6, 2, 1)":"substr($6, 3, 2)

        # "den" column
        if ($5 ==  0)
           $5="Po"
        else if ($5 == 1)
           $5="Ut"
        else if ($5 == 2)
           $5="St"
        else if ($5 == 3)
           $5="Čt"
        else if ($5 == 4)
           $5="Pa"
        else if ($5 == 5)
           $5="So"
        else if ($5 == 6)
           $5="Ne"

        # "nasledky" column
        if ($14 > 0)
           $16="usmrceno osob"
        else if ($15 > 0)
          $16="těžce zraněno osob"
        else if ($16 > 0)
          $16="lehce zraněno osob"
        else if ($16 == 0)
          $16="bez zranění osob"

        # "zavineni" column
        if ($11 == 0)
          $11="jiné zavinění"
        else if ($11 == 1)
           $11="řidičem motorového vozidla"
        else if ($11 == 2)
          $11="řidičem nemotorového vozidla"
        else if ($11 == 3)
          $11="chodcem"
        else if ($11 == 4)
          $11="lesní zvěří, domácím zvířectvem"
        else if ($11 == 5)
          $11="jiným účastníkem silničního provozu"
        else if ($11 == 6)
          $11="závadou komunikace"
        else if ($11 == 7)
          $11="technickou závadou vozidla"

        # "vozidlo" column
        if ($33 == 0 || $33 == 00)
           $33="moped"
        else if ($33 == 1)
          $33="malý motocykl (do 50 ccm)"
        else if ($33 == 2)
          $33="motocykl (včetně sidecarů, skútrů apod.)"
        else if ($33 == 3)
          $33="osobní automobil bez přívěsu"
        else if ($33 == 4)
          $33="osobní automobil s přívěsem"
        else if ($33 == 5)
          $33="nákladní automobil (včetně multikáry, autojeřábu, cisterny atd.)"
        else if ($33 == 6)
          $33="nákladní automobil s přívěsem"
        else if ($33 == 7)
          $33="nákladní automobil s návěsem"
        else if ($33 == 8)
          $33="autobus"
        else if ($33 == 9)
          $33="traktor (i s přívěsem)"
        else if ($33 == 10)
          $33="tramvaj"
        else if ($33 == 11)
          $33="trolejbus"
        else if ($33 == 12)
          $33="jiné motorové vozidlo (zemědělské, lesní, stavební stroje atd.)"
        else if ($33 == 13)
          $33="jízdní kolo"
        else if ($33 == 14)
          $33="povoz, jízda na koni"
        else if ($33 == 15)
          $33="jiné nemotorové vozidlo"
        else if ($33 == 16)
          $33="vlak"
        else if ($33 == 17)
          $33="nezjištěno, řidič ujel"
        else if ($33 == 18)
          $33="jiný druh vozidla"

        # "x" coordinate column, empty value -> empty quotes "" (length 2)
        if (length($48) == 2)
          next

        # "y" coordinate column, empty value -> empty quotes "" (length 2)
        if (length($49) == 2)
          next

        print $4,$5,$6,$16,$11,$33,$48,$49}'"'"' $file | sed  "s/,/./g" >> $ACCIDENTS_CSV_FILE
    fi
done' sh {} +

if [ -f $ACCIDENTS_CSV_FILE ]; then
    # Clean duplicates
    CLEANED_FILE="${ACCIDENTS_CSV_FILE}.cleaned"
    awk '!visited[$0]++' $ACCIDENTS_CSV_FILE > $CLEANED_FILE
    mv $CLEANED_FILE $ACCIDENTS_CSV_FILE

    # Virtual layer for csv file with columns definition
    echo "<OGRVRTDataSource>
        <OGRVRTLayer name=\"${ACCIDENTS_CSV_FILE_BASENAME}\">
            <SrcDataSource>${ACCIDENTS_CSV_FILE}</SrcDataSource>
            <GeometryField encoding=\"PointFromColumns\" x=\"x\" y=\"y\"/>
            <GeometryType>wkbPoint</GeometryType>
            <LayerSRS>EPSG:5514</LayerSRS>
            <OpenOptions>
                <OOI key=\"EMPTY_STRING_AS_NULL\">YES</OOI>
            </OpenOptions>
            <Field name=\"datum\" type=\"Date\" nullable=\"true\" />
            <Field name=\"den\" type=\"String\" nullable=\"true\" />
            <Field name=\"cas\" type=\"Time\" nullable=\"true\" />
            <Field name=\"nasledky\" type=\"String\" nullable=\"true\" />
            <Field name=\"zavineni\" type=\"String\" nullable=\"true\" />
            <Field name=\"vozidlo\" type=\"String\" nullable=\"true\" />
            <Field name=\"x\" type=\"Real\" nullable=\"true\" />
            <Field name=\"y\" type=\"Real\" nullable=\"true\" />
        </OGRVRTLayer>
    </OGRVRTDataSource>" > "$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}.vrt"

    # ogr2ogr -dialect SQLite -sql "${SQL}" -nln "${ACCIDENTS_CSV_FILE_BASENAME}" -s_srs EPSG:5514 -t_srs EPSG:4326 $ACCIDENTS_SPATIALLITE $ACCIDENTS_CSV_FILE

    ogr2ogr -t_srs EPSG:4326 -f SQLite $ACCIDENTS_SPATIALLITE $ACCIDENTS_VRT_FILE
fi
