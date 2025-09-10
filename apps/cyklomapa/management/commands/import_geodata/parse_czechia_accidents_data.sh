#!/usr/bin/env bash

: '
Concatenate, reclassify Czechia accidents data (CSV files) and convert
them into SQLITE db (geospatial layer). Transform them from EPSG 5514
(S-JTSK) to the EPS 4326 (WGS-84).
'

TEMP_DIR=$1
export ACCIDENTS_CSV_FILE=$2
ACCIDENTS_SPATIALLITE=$3

COLS="id;\
identifikacni_cislo;\
datum;\
den;\
cas;\
druh;\
druh_srazky_jedoucich_vozidel;\
lokalita;\
nasledky;\
zavineni;\
alkohol_u_vinika_nehody_pritomen;\
priciny;\
druh_povrchu_vozovky;\
stav_povrchu_vozovky_v_dobe_nehody;\
stav_komunikace;\
viditelnost;\
deleni_komunikace;\
situovani;\
rizeni_provozu_v_dobe_nehody;\
mistni_uprava_prednosti_v_jizde;\
specificka_mista_a_objekty_v_miste_nehody;\
smerove_pomery;\
pocet_zucastnenych_vozidel;\
misto_dopravni_nehody;\
druh_pozemni_komunikace;\
druh_krizujici_komunikace;\
druh_vozidla;\
charakteristika_vozidla;\
smyk;\
vozidlo_po_nehode;\
smer_jizdy_nebo_postaveni_vozidla;\
stav_ridice;\
vnejsi_ovlivneni_ridice;\
x;\
y;\
kategorie_chodce;\
chovani_chodce;\
situace_v_miste_nehody"

export EMPTY_VALUE="''"
export CSV_FILE_SEPARATOR=";"

export ACCIDENTS_CSV_FILE_BASENAME=$(basename $ACCIDENTS_CSV_FILE .csv)
ACCIDENTS_JOIN_CSV_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}_join.csv"
export ACCIDENTS_JOIN_CSV_FILE_BASENAME=$(basename $ACCIDENTS_JOIN_CSV_FILE)
ACCIDENTS_VRT_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}.vrt"
ACCIDENTS_CHODCI_CSV_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}_chodci.csv"
export ACCIDENTS_CHODCI_CSV_FILE_BASENAME=$(basename $ACCIDENTS_CHODCI_CSV_FILE)
# LAYER_COLS=$(echo $COLS | cut -d ";" -f1-6 | sed "s/;/, /g")
# SQL="SELECT ${LAYER_COLS}, MakePoint(CAST(x AS float),CAST(y AS float)) FROM $(basename ${ACCIDENTS_CSV_FILE} )"

# Columns descriptions https://www.policie.cz/soubor/polozky-formulare-hlavicky-souboru-xlsx.aspx
# Parsing data until to the 2023 year
find "$TEMP_DIR" -type d -name 'ext_*' -exec bash -c '
for csv_base_dir do
    ./parse_czechia_accidents_data_until_2023.sh \
        $csv_base_dir \
        "${csv_base_dir}/${ACCIDENTS_CSV_FILE_BASENAME}.csv" \
        "${csv_base_dir}/${ACCIDENTS_JOIN_CSV_FILE_BASENAME}" \
        "${csv_base_dir}/${ACCIDENTS_CHODCI_CSV_FILE_BASENAME}" \
        $EMPTY_VALUE \
       	$CSV_FILE_SEPARATOR
done' sh {} +

# Convert new XLSX file format (since 2023 year) to the CSV file format
find "$TEMP_DIR" -type f -name '*.xlsx' -exec bash -c '
for file do
    filename=$(basename -- "$file")
    filename="${filename%.*}"
    dirname=$(dirname "$file")
    csv_file_path="${dirname}/${filename}.csv"
    xlsx2csv -d $CSV_FILE_SEPARATOR $file $csv_file_path
    sed -i -e '1,7d' $csv_file_path
done' sh {} +

# Convert new XLS file format (since 2023 year) to the CSV file format
find "$TEMP_DIR" -type f -name '*.xls' -exec bash -c '
for file do
    filename=$(basename -- "$file")
    filename="${filename%.*}"
    dirname=$(dirname "$file")
    csv_file_path="${dirname}/${filename}.csv"
    htmltab -e ";" -o $csv_file_path $file
    sed -i '1d' $csv_file_path
done' sh {} +

# Parsing data since 2023 year
find "$TEMP_DIR" -type d -name 'ext_*' -exec bash -c '
for csv_base_dir do
    ./parse_czechia_accidents_data_since_2023.sh \
        $csv_base_dir \
        "${csv_base_dir}/${ACCIDENTS_JOIN_CSV_FILE_BASENAME}" \
        $EMPTY_VALUE \
	$CSV_FILE_SEPARATOR
done' sh {} +

# Concatenate individuals all accidents CSV files into one accidents result file
ACCIDENTS_CSV_FILES=$(find "$TEMP_DIR" -type f -name $(basename $ACCIDENTS_CSV_FILE)  -printf '%p ')
cat $ACCIDENTS_CSV_FILES > $ACCIDENTS_CSV_FILE

# Fullfill ID column with IDs
gawk -i inplace '{printf "%s;%s\n", NR,$0}' $ACCIDENTS_CSV_FILE
# Add columns names first row
gawk -v cols="$COLS" -i inplace 'BEGINFILE{print cols}{print}' $ACCIDENTS_CSV_FILE

if [ -f $ACCIDENTS_CSV_FILE ]; then
    # Clean duplicates
    # CLEANED_FILE="${ACCIDENTS_CSV_FILE}.cleaned"
    # awk '!visited[$0]++' $ACCIDENTS_CSV_FILE > $CLEANED_FILE
    # mv $CLEANED_FILE $ACCIDENTS_CSV_FILE

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
            <Field name=\"id\" type=\"Integer\" nullable=\"false\" />
            <Field name=\"identifikacni_cislo\" type=\"String\" nullable=\"true\" />
            <Field name=\"datum\" type=\"Date\" nullable=\"true\" />
            <Field name=\"den\" type=\"String\" nullable=\"true\" />
            <Field name=\"cas\" type=\"Time\" nullable=\"true\" />
            <Field name=\"druh_srazky_jedoucich_vozidel\" type=\"String\" nullable=\"true\" />
            <Field name=\"druh\" type=\"String\" nullable=\"true\" />
            <Field name=\"lokalita\" type=\"String\" nullable=\"true\" />
            <Field name=\"nasledky\" type=\"String\" nullable=\"true\" />
            <Field name=\"zavineni\" type=\"String\" nullable=\"true\" />
            <Field name=\"alkohol_u_vinika_nehody_pritomen\" type=\"String\" nullable=\"true\" />
            <Field name=\"priciny\" type=\"String\" nullable=\"true\" />
            <Field name=\"druh_povrchu_vozovky\" type=\"String\" nullable=\"true\" />
            <Field name=\"stav_povrchu_vozovky_v_dobe_nehody\" type=\"String\" nullable=\"true\" />
            <Field name=\"stav_komunikace\" type=\"String\" nullable=\"true\" />
            <Field name=\"viditelnost\" type=\"String\" nullable=\"true\" />
            <Field name=\"deleni_komunikace\" type=\"String\" nullable=\"true\" />
            <Field name=\"situovani\" type=\"String\" nullable=\"true\" />
            <Field name=\"rizeni_provozu_v_dobe_nehody\" type=\"String\" nullable=\"true\" />
            <Field name=\"mistni_uprava_prednosti_v_jizde\" type=\"String\" nullable=\"true\" />
            <Field name=\"specificka_mista_a_objekty_v_miste_nehody\" type=\"String\" nullable=\"true\" />
            <Field name=\"smerove_pomery\" type=\"String\" nullable=\"true\" />
            <Field name=\"pocet_zucastnenych_vozidel\" type=\"Integer\" nullable=\"true\" />
            <Field name=\"misto_dopravni_nehody\" type=\"String\" nullable=\"true\" />
            <Field name=\"druh_pozemni_komunikace\" type=\"String\" nullable=\"true\" />
            <Field name=\"druh_krizujici_komunikace\" type=\"String\" nullable=\"true\" />
            <Field name=\"kategorie_chodce\" type=\"String\" nullable=\"true\" />
            <Field name=\"chovani_chodce\" type=\"String\" nullable=\"true\" />
            <Field name=\"situace_v_miste_nehody\" type=\"String\" nullable=\"true\" />
            <Field name=\"druh_vozidla\" type=\"String\" nullable=\"true\" />
            <Field name=\"charakteristika_vozidla\" type=\"String\" nullable=\"true\" />
            <Field name=\"smyk\" type=\"String\" nullable=\"true\" />
            <Field name=\"vozidlo_po_nehode\" type=\"String\" nullable=\"true\" />
            <Field name=\"smer_jizdy_nebo_postaveni_vozidla\" type=\"String\" nullable=\"true\" />
            <Field name=\"stav_ridice\" type=\"String\" nullable=\"true\" />
            <Field name=\"vnejsi_ovlivneni_ridice\" type=\"String\" nullable=\"true\" />
            <Field name=\"x\" type=\"Real\" nullable=\"true\" />
            <Field name=\"y\" type=\"Real\" nullable=\"true\" />
        </OGRVRTLayer>
    </OGRVRTDataSource>" > "$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}.vrt"

    # ogr2ogr -dialect SQLite -sql "${SQL}" -nln "${ACCIDENTS_CSV_FILE_BASENAME}" -s_srs EPSG:5514 -t_srs EPSG:4326 $ACCIDENTS_SPATIALLITE $ACCIDENTS_CSV_FILE

    ogr2ogr -t_srs EPSG:4326 -f SQLite $ACCIDENTS_SPATIALLITE $ACCIDENTS_VRT_FILE
fi
