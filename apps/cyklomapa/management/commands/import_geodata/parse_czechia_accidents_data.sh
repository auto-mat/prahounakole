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

        # hlavní příčiny nehody
        if ($13 == 100)
          $13="nezaviněná řidičem"
        else if ($13 == 201)
          $13="nepřizpůsobení rychlosti - intenzitě (hustotě) provozu"
        else if ($13 == 202)
          $13="nepřizpůsobení rychlosti - viditelnosti (mlha, soumrak, jízda v noci na tlumená světla apod.)"
        else if ($13 == 203)
          $13="nepřizpůsobení rychlosti - vlastnostem vozidla a nákladu"
        else if ($13 == 204)
          $13="nepřizpůsobení rychlosti - stavu vozovky (náledí, výtluky, bláto, mokrý povrch apod.)"
        else if ($13 == 205)
          $13="nepřizpůsobení rychlosti - dopravně technickému stavu vozovky (zatáčka, klesání, stoupání, šířka vozovky apod.)"
        else if ($13 == 206)
          $13="překročení předepsané rychlosti stanovené pravidly"
        else if ($13 == 207)
          $13="překročení rychlosti stanovené dopravní značkou"
        else if ($13 == 208)
          $13="nepřizpůsobení rychlosti - bočnímu, nárazovému větru (i při míjení, předjíždění vozidel)"
        else if ($13 == 209)
          $13="jiný druh nepřiměřené rychlosti"
        else if ($13 == 301)
          $13="předjíždění - vpravo"
        else if ($13 == 302)
          $13="předjíždění - bez dostatečného bočního odstupu"
        else if ($13 == 303)
          $13="předjíždění - bez dostatečného rozhledu (v nepřehledné zatáčce nebo její blízkosti, před vrcholem stoupání apod.)"
        else if ($13 == 304)
          $13="předjíždění - došlo k ohrožení protijedoucího řidiče vozidla (špatný odhad vzdálenosti potřebné k předjetí apod.)"
        else if ($13 == 305)
          $13="předjíždění - došlo k ohrožení předjížděného řidiče vozidla (vynucené zařazení, předjížděný řidič musel prudce brzdit, měnit směr jízdy apod.)"
        else if ($13 == 306)
          $13="předjíždění - vlevo vozidla odbočujícího vlevo"
        else if ($13 == 307)
          $13="předjíždění - v místech, kde je to zakázáno dopravní značkou"
        else if ($13 == 308)
          $13="předjíždění - byla přejeta podélná čára souvislá"
        else if ($13 == 309)
          $13="bránění v předjíždění"
        else if ($13 == 310)
          $13="přehlédnutí již předjíždějícícho souběžně jedoucího vozidla"
        else if ($13 == 311)
          $13="jiný druh nesprávného předjíždění"
        else if ($13 == 401)
          $13="jízda na červenou 3-barevného semaforu"
        else if ($13 == 402)
          $13="proti příkazu dopravní značky - stůj dej přednost"
        else if ($13 == 403)
          $13="proti příkazu dopravní značky - dej přednost"
        else if ($13 == 404)
          $13="vozidlu přijíždějícímu zprava"
        else if ($13 == 405)
          $13="při odbočování vlevo"
        else if ($13 == 406)
          $13="tramvají, která odbočuje"
        else if ($13 == 407)
          $13="protijedoucímu vozidlu při objíždění překážky"
        else if ($13 == 408)
          $13="při zařazování do proudu jedoucích vozidel ze stanice, místa zastavení nebo stání"
        else if ($13 == 409)
          $13="při vjíždění na silnici"
        else if ($13 == 410)
          $13="při otáčení nebo couvání"
        else if ($13 == 411)
          $13="při přejíždění z jednoho jízdního pruhu do druhého"
        else if ($13 == 412)
          $13="chodci na vyznačeném přechodu"
        else if ($13 == 413)
          $13="při odbočování vlevo - souběžně jedoucímu vozidlu"
        else if ($13 == 414)
          $13="jiné nedání přednosti"
        else if ($13 == 501)
          $13="jízda po nesprávné straně vozovky, vjetí do protisměru"
        else if ($13 == 502)
          $13="vyhýbání bez dostatečného bočního odstupu (vůle)"
        else if ($13 == 503)
          $13="nedodržení bezpečné vzdálenosti za vozidlem"
        else if ($13 == 504)
          $13="nesprávné otáčení nebo couvání"
        else if ($13 == 505)
          $13="chyby při udání směru jízdy"
        else if ($13 == 506)
          $13="bezohledná, agresivní, neohleduplná jízda"
        else if ($13 == 507)
          $13="náhlé bezdůvodné snížení rychlosti jízdy, zabrzdění nebo zastavení"
        else if ($13 == 508)
          $13="řidič se plně nevěnoval řízení vozidla"
        else if ($13 == 509)
          $13="samovolné rozjetí nezajištěného vozidla"
        else if ($13 == 510)
          $13="vjetí na nezpevněnou komunikaci"
        else if ($13 == 511)
          $13="nezvládnutí řízení vozidla"
        else if ($13 == 512)
          $13="jízda (vjetí) jednosměrnou ulicí, silnicí (v protisměru)"
        else if ($13 == 513)
          $13="nehoda v důsledku  použití (policií) prostředků k násilnému zastavení vozidla (zastavovací pásy, zábrana, vozidlo atp.)"
        else if ($13 == 514)
          $13="nehoda v důsledku použití služební zbraně (policií)"
        else if ($13 == 515)
          $13="nehoda při provádění služebního zákroku (pronásledování pachatele atd.)"
        else if ($13 == 516)
          $13="jiný druh nesprávného způsobu jízdy"
        else if ($13 == 601)
          $13="závada řízení"
        else if ($13 == 602)
          $13="závada provozní brzdy"
        else if ($13 == 603)
          $13="neúčinná nebo nefungující parkovací brzda"
        else if ($13 == 604)
          $13="opotřebení běhounu pláště pod stanovenou mez"
        else if ($13 == 605)
          $13="defekt pneumatiky způsobený průrazem nebo náhlým únikem vzduchu"
        else if ($13 == 606)
          $13="závada osvětlovací soustavy vozidla (neúčinná, chybějící, znečištěná apod.)"
        else if ($13 == 607)
          $13="nepřipojená nebo poškozená spojovací hadice pro bzrdění přípojného vozidla"
        else if ($13 == 608)
          $13="nesprávné uložení nákladu"
        else if ($13 == 609)
          $13="upadnutí, ztráta kola vozidla (i rezervního)"
        else if ($13 == 610)
          $13="zablokování kol v důsledku mechanické závady vozidla (zadřený motor, převodovka, rozvodovka, spadlý řetěz apod.)"
        else if ($13 == 611)
          $13="lom závěsu kola, pružiny"
        else if ($13 == 612)
          $13="nezajištěná nebo poškozená bočnice (i u přívěsu)"
        else if ($13 == 613)
          $13="závada závěsu pro přívěs"
        else if ($13 == 614)
          $13="utržená spojovací hřídel"
        else if ($13 == 615)
          $13="jiná technická závada (vztahuje se i na přípojná vozidla)"

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

        print $4,$5,$6,$16,$11,$13,$33,$48,$49}'"'"' $file | sed  "s/,/./g" >> $ACCIDENTS_CSV_FILE
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
            <Field name=\"priciny_nehody\" type=\"String\" nullable=\"true\" />
            <Field name=\"vozidlo\" type=\"String\" nullable=\"true\" />
            <Field name=\"x\" type=\"Real\" nullable=\"true\" />
            <Field name=\"y\" type=\"Real\" nullable=\"true\" />
        </OGRVRTLayer>
    </OGRVRTDataSource>" > "$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}.vrt"

    # ogr2ogr -dialect SQLite -sql "${SQL}" -nln "${ACCIDENTS_CSV_FILE_BASENAME}" -s_srs EPSG:5514 -t_srs EPSG:4326 $ACCIDENTS_SPATIALLITE $ACCIDENTS_CSV_FILE

    ogr2ogr -t_srs EPSG:4326 -f SQLite $ACCIDENTS_SPATIALLITE $ACCIDENTS_VRT_FILE
fi
