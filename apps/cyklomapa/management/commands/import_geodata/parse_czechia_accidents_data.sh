#!/usr/bin/env bash

: '
Concatenate, reclassify Czechia accidents data (CSV files) and convert
them into SQLITE db (geospatial layer). Transform them from EPSG 5514
(S-JTSK) to the EPS 4326 (WGS-84).
'

TEMP_DIR=$1
export ACCIDENTS_CSV_FILE=$2
ACCIDENTS_SPATIALLITE=$3

COLS="identifikacni_cislo;\
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

ACCIDENTS_CSV_FILE_BASENAME=$(basename $ACCIDENTS_CSV_FILE .csv)
ACCIDENTS_JOIN_CSV_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}_join.csv"
ACCIDENTS_VRT_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}.vrt"
export ACCIDENTS_CHODCI_CSV_FILE="$(dirname ${ACCIDENTS_CSV_FILE})/${ACCIDENTS_CSV_FILE_BASENAME}_chodci.csv"
# LAYER_COLS=$(echo $COLS | cut -d ";" -f1-6 | sed "s/;/, /g")
# SQL="SELECT ${LAYER_COLS}, MakePoint(CAST(x AS float),CAST(y AS float)) FROM $(basename ${ACCIDENTS_CSV_FILE} )"

# Columns descriptions https://www.policie.cz/soubor/polozky-formulare-hlavicky-souboru-xlsx.aspx
find "$TEMP_DIR" -type f -name '*.csv' ! -name "$(basename ${ACCIDENTS_CSV_FILE})" -exec bash -c '
FILTER=(08.csv,09.csv,10.csv,11.csv,12.csv,13.csv,CHODCI.csv)
for file do
    if [[ ! "${FILTER}" =~ "$(basename "${file}")" ]]; then
       gawk -F ";" '"'"'
       BEGIN {OFS=";"}
      {
        # "druh_pozemni_komunikace" column
        if ($2 == 0)
          $2="dálnice"
        else if ($2 == 1)
          $2="silnice 1. třídy"
        else if ($2 == 2)
          $2="silnice 2. třídy"
        else if ($2 == 3)
          $2="silnice 3. třídy"
        else if ($2 == 4)
          $2="uzel - tj. křižovatka sledovaná ve vybraných městech"
        else if ($2 == 5)
          $2="komunikace sledovaná - (ve vybraných městech)"
        else if ($2 == 6)
          $2="komunikace místní"
        else if ($2 == 7)
          $2="komunikace účelová - polní a lesní cesty atd."
        else if ($2 == 8)
          $2="komunikace účelová - ostatní (parkoviště, odpočívky apod.)"
        else
          $2=""

        # "cas" column
        if ($6 == "\"2560\"")
          $6=""
        else if (length($6) == 6)
          $6=substr($6, 2, 2)":"substr($6, 4, 2)
        else
          $6=substr($6, 2, 1)":"substr($6, 3, 2)

        # "den" column
        if ($5 == 0)
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
        else
          $5=""

        # "druh" column
        if ($7 == 0)
          $7="jiný druh nehody"
        if ($7 == 1)
          $7="srážka s jedoucím nekolejovým vozidlem"
        else if ($7 == 2)
          $7="srážka s vozidlem zaparkovaným, odstaveným"
        else if ($7 == 3)
          $7="srážka s pevnou překážkou"
        else if ($7 == 4)
          $7="srážka s chodcem"
        else if ($7 == 5)
          $7="s lesní zvěří"
        else if ($7 == 6)
          $7="s domácím zvířetem"
        else if ($7 == 7)
          $7="s vlakem"
        else if ($7 == 8)
          $7="s tramvají"
        else if ($7 == 9)
          $7="havárie"
        else
          $7=""

        # "druh_srazky_jedoucich_vozidel" column
        if ($8 == 0)
          $8="nepřichází v úvahu (nejedná se o srážku jedoucích vozidel)"
        else if ($8 == 1)
          $8="čelní"
        else if ($8 == 2)
          $8="boční"
        else if ($8 == 3)
          $8="z boku"
        else if ($8 == 4)
          $8="zezadu"
        else
          $8=""

        # "lokalita" column
        if (substr($64, 2, 1) == 1)
          $64="v obci"
        else if (substr($64, 2, 1) == 2)
          $64="mimo obec"
        else
          $64=""

        # "nasledky" column
        if ($14 > 0)
          $16="usmrceno osob"
        else if ($15 > 0)
          $16="těžce zraněno osob"
        else if ($16 > 0)
          $16="lehce zraněno osob"
        else if ($16 == 0)
          $16="bez zranění osob"
        else
          $16=""

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
        else
          $11=""

        # "alkohol_u_vinika_nehody_pritomen" column
        if ($12 == 0)
          $12="nezjišťováno"
        else if ($12 == 1)
          $12="ano (obsah alkoholu v krvi do 0,24 ‰)"
        else if ($12 == 2)
          $12="ne"
        else if ($12 == 3)
          $12="ano (obsah alkoholu v krvi od 0,24 ‰ do 0,5 ‰)"
        else if ($12 == 4)
          $12="pod vlivem drog"
        else if ($12 == 5)
          $12="pod vlivem alkoholu a drog"
        else if ($12 == 6)
          $12="ano (obsah alkoholu v krvi od 0,5 ‰ do 0,8 ‰)"
        else if ($12 == 7)
          $12="ano (obsah alkoholu v krvi od 0,8 ‰ do 1,0 ‰)"
        else if ($12 == 8)
          $12="ano (obsah alkoholu v krvi od 1,0 ‰ do 1,5 ‰)"
        else if ($12 == 9)
          $12="ano (obsah alkoholu v krvi 1,5 ‰ a více)"
        else
          $12=""

        # "priciny" column
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
        else
          $13=""

        # "druh_povrchu_vozovky" column
        if ($18 == 1)
          $18="dlažba"
        else if ($18 == 2)
          $18="živice"
        else if ($18 == 3)
          $18="beton"
        else if ($18 == 4)
          $18="panely"
        else if ($18 == 5)
          $18="štěrk"
        else if ($18 == 6)
          $18="jiný nezpevněný povrch"
        else
          $18=""

        # "stav_povrchu_vozovky_v_dobe_nehody" column
        if ($19 == 0)
          $19="jiný stav povrchu vozovky v době nehody"
        else if ($19 == 1)
          $19="povrch suchý - neznečištěný"
        else if ($19 == 2)
          $19="povrch suchý - znečištěný (písek, prach, listí, štěrk atd.)"
        else if ($19 == 3)
          $19="povrch mokrý"
        else if ($19 == 4)
          $19="na vozovce je bláto"
        else if ($19 == 5)
          $19="na vozovce je náledí, ujetý sníh - posypané"
        else if ($19 == 6)
          $19="na vozovce je náledí, ujetý sníh - neposypané"
        else if ($19 == 7)
          $19="na vozovce je rozlitý olej, nafta apod."
        else if ($19 == 8)
          $19="souvislá sněhová vrstva, rozbředlý sníh"
        else if ($19 == 9)
          $19="náhlá změna stavu vozovky (námraza na mostu, místní náledí)"
        else
          $19=""

        # "stav_komunikace" column
        if ($20 == 1)
          $20="dobrý, bez závad"
        else if ($20 == 2)
          $20="podélný sklon vyšší než 8 %"
        else if ($20 == 3)
          $20="nesprávně umístěná, znečištěná, chybějící dopravní značka"
        else if ($20 == 4)
          $20="zvlněný povrch v podélném směru"
        else if ($20 == 5)
          $20="souvislé výtluky"
        else if ($20 == 6)
          $20="nesouvislé výtluky"
        else if ($20 == 7)
          $20="trvalé zúžení vozovky"
        else if ($20 == 8)
          $20="příčná stružka, hrbol, vystouplé, propadlé kolejnice"
        else if ($20 == 9)
          $20="neoznačená nebo nedostatečně označená překážka na komunikaci"
        else if ($20 == 10)
          $20="přechodná uzavírka jednoho jízdního pruhu"
        else if ($20 == 11)
          $20="přechodná uzavírka komunikace nebo jízdního pásu"
        else if ($20 == 12)
          $20="jiný (neuvedený) stav nebo závada komunikace"
        else
          $20=""

        # "viditelnost" column
        if ($22 == 1)
          $22="ve dne - viditelnost nezhoršená vlivem povětrnostních podmínek"
        else if ($22 == 2)
          $22="ve dne - zhoršená viditelnost (svítání, soumrak)"
        else if ($22 == 3)
          $22="ve dne - zhoršená viditelnost vlivem povětrnostních podmínek (mlha, sněžení, déšť apod.)"
        else if ($22 == 4)
          $22="v noci - s veřejným osvětlením, viditelnost nezhoršená vlivem povětrnostních podmínek"
        else if ($22 == 5)
          $22="v noci - s veřejným osvětlením, zhoršená viditelnost vlivem povětrnostních podmínek (mlha, déšť, sněžení apod.)"
        else if ($22 == 6)
          $22="v noci - bez veřejného osvětlení, viditelnost nezhoršená vlivem povětrnostních podmínek"
        else if ($22 == 7)
          $22="v noci - bez veřejného osvětlení, viditelnost zhoršená vlivem povětrnostních podmínek (mlha, déšť, sněžení apod.)"
        else
          $22=""

        # "deleni_komunikace" column
        if ($24 == 0)
          $24="žádná z uvedených"
        else if ($24 == 1)
          $24="dvoupruhová"
        else if ($24 == 2)
          $24="třípruhová"
        else if ($24 == 3)
          $24="čtyřpruhová s dělícím pásem"
        else if ($24 == 4)
          $24="čtyřpruhová s dělící čarou"
        else if ($24 == 5)
          $24="vícepruhová"
        else if ($24 == 6)
          $24="rychlostní komunikace"
        else
          $24=""

        # "situovani" column
        if ($25 == 0)
          $25="žádné z uvedených"
        else if ($25 == 1)
          $25="na jízdním pruhu"
        else if ($25 == 2)
          $25="na odstavném pruhu"
        else if ($25 == 3)
          $25="na krajnici"
        else if ($25 == 4)
          $25="na odbočovacím, připojovacím pruhu"
        else if ($25 == 5)
          $25="na pruhu pro pomalá vozidla"
        else if ($25 == 6)
          $25="na chodníku nebo ostrůvku"
        else if ($25 == 7)
          $25="na kolejích tramvaje"
        else if ($25 == 8)
          $25="mimo komunikaci"
        else if ($25 == 9)
          $25="na stezce pro cyklisty"
        else
          $25=""

        # "rizeni_provozu_v_dobe_nehody" column
        if ($26 == 0)
          $26="žádný způsob řízení provozu"
        else if ($26 == 1)
          $26="policistou nebo jiným pověřeným orgánem"
        else if ($26 == 2)
          $26="světelným signalizačním zařízením"
        else if ($26 == 3)
          $26="místní úprava (vyplní se místní úprava přednosti v jízdě)"
        else
          $26=""

        # "mistni_uprava_prednosti_v_jizde" column
        if ($27 == 0)
          $27="žádná místní úprava"
        else if ($27 == 1)
          $27="světelná signalilzace přepnuta na přerušovanou žlutou"
        else if ($27 == 2)
          $27="světelná signalizace mimo provoz"
        else if ($27 == 3)
          $27="přednost vyznačena dopravními značkami"
        else if ($27 == 4)
          $27="přednost vyznačena přenosnými dopravními značkami nebo zařízením"
        else if ($27 == 5)
          $27="přednost nevyznačena - vyplývá z pravidel silníčního provozu"
        else
          $27=""

        # "specificka_mista_a_objekty_v_miste_nehody" column
        if ($28 == 0)
          $28="žádné nebo žádné z uvedených"
        else if ($28 == 1)
          $28="přechod pro chodce"
        else if ($28 == 2)
          $28="v blízkosti přechodu pro chodce (do vzdálenosti 20 m)"
        else if ($28 == 3)
          $28="železniční přejezd nezabezpečený závorami ani světelným výstražným zařízením"
        else if ($28 == 4)
          $28="železniční přejezd zabezpečený"
        else if ($28 == 5)
          $28="most, nadjezd, podjezd, tunel"
        else if ($28 == 6)
          $28="zastávka autobusu, trolejbusu, tramvaje s nástup. ostrůvkem"
        else if ($28 == 7)
          $28="zastávka tramvaje, autobusu, trolejbusu bez nástup. ostrůvku"
        else if ($28 == 8)
          $28="výjezd z parkoviště, lesní cesty apod. (pol. 36 = 7,8)"
        else if ($28 == 9)
          $28="čerpadlo pohonných hmot"
        else if ($28 == 10)
          $28="parkoviště přiléhající ke komunikaci"
        else
          $28=""

        # "smerove_pomery" column
        if ($29 == 1)
          $29="přímý úsek"
        else if ($29 == 2)
          $29="přímý úsek po projetí zatáčkou (do vzdálenosti cca 100 m od optického konce zatáčky)"
        else if ($29 == 3)
          $29="zatáčka"
        else if ($29 == 4)
          $29="křižovatka průsečná - čtyřramenná"
        else if ($29 == 5)
          $29="křižovatka styková - tříramenná"
        else if ($29 == 6)
          $29="křižovatka pěti a víceramenná"
        else if ($29 == 7)
          $29="kruhový objezd"
        else
          $29=""

        # "misto_dopravni_nehody" column
        if ($31 == 00)
          $31="mimo křižovatku"
        else if ($31 == 10)
          $31="na kžižovatce - jedná-li se o křížení místních komunikací, účelových komunikací nebo jde o mezilehlou křižovatku (na sledovaném úseku ve sledovaných městech)"
        else if ($31 == 11 || $31 == 12 || $31 == 13 || $31 == 14 || $31 == 15 || $31 == 16 || $31 == 17 || $31 == 18)
          $31="uvnitř zóny 1-8 předmětné křižovatky"
        else if ($31 == 19)
          $31="na křižovatce - uvnitř hranic křižovatky definovaných pro systém evidence nehod (zóna 9)"
        else if ($31 == 22 || $31 == 23 || $31 == 24 || $31 == 25 || $31 == 26 || $31 == 27 || $31 == 28)
          $31="na vjezdové nebo výjezdové části větve při mimoúrovňovém křížení"
        else if ($31 == 29)
          $31="mimo zónu - uvnitř zóny 1-8 předmětné křižovatky, na křižovatce - uvnitř hranic křižovatky definovaných pro systém evidence nehod (zóna 9) a na vjezdové nebo výjezdové části větve při mimoúrovňovém křížení"
        else
          $31=""

        # "druh_krizujici_komunikace" column
        if ($32 == 1)
          $32="silnice 1. třídy"
        else if ($32 == 2)
          $32="silnice 2. třídy"
        else if ($32 == 3)
          $32="silnice 3. třídy"
        else if ($32 == 6)
          $32="místní komunikace"
        else if ($32 == 7)
          $32="účelová komunikace"
        else if ($32 == 9)
          $32="větev mimoúrovňové křižovatky"
        else
          $32=""

        # "druh_vozidla" column
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
        else
          $33=""

        # "charakteristika_vozidla" column
        if ($36 == 00)
          $36="nezjištěno"
        else if ($36 == 1)
          $36="soukromé - nevyužívané k výdělečné činnost"
        else if ($36 == 2)
          $36="soukromé - využívané k výdělečné činnosti"
        else if ($36 == 3)
          $36="soukromá organizace - (podnikatel, s.r.o., v.o.s., a.s., atd.)"
        else if ($36 == 4)
          $36="veřejná hromadná doprava"
        else if ($36 == 5)
          $36="městská hromadná doprava"
        else if ($36 == 6)
          $36="mezinárodní kamionová doprava"
        else if ($36 == 7)
          $36="TAXI"
        else if ($36 == 8)
          $36="státní podnik, státní organizace"
        else if ($36 == 9)
          $36="registrované mimo území ČR"
        else if ($36 == 10)
          $36="zastupitelský úřad"
        else if ($36 == 11)
          $36="ministerstvo vnitra"
        else if ($36 == 12)
          $36="policie ČR"
        else if ($36 == 13)
          $36="městská, obecní policie"
        else if ($36 == 14)
          $36="soukromé bezpečnostní agentury"
        else if ($36 == 15)
          $36="ministerstvo obrany"
        else if ($36 == 16)
          $36="jiné"
        else if ($36 == 17)
          $36="odcizené"
        else if ($36 == 18)
          $36="vozidlo AUTOŠKOLY provádějící výcvik"
        else
          $36=""

        # "smyk" column
        if ($37 == 0)
          $37="ne"
        else if ($37 == 1)
          $37="ano"
        else
          $37=""

        # "vozidlo_po_nehode" column
        if ($38 == 0)
          $38="žádná z uvedených"
        else if ($38 == 1)
          $38="nedošlo k požáru"
        else if ($38 == 2)
          $38="došlo k požáru"
        else if ($38 == 3)
          $38="řidič ujel - zjištěn"
        else if ($38 == 4)
          $38="řidič ujel (utekl) - nezjištěn"
        else
          $38=""

        # "smer_jizdy_nebo_postaveni_vozidla" column
        if ($42 == 1)
          $42="vozidlo jedoucí - ve měru staničení (na komunikaci)"
        else if ($42 == 2)
          $42="vozidlo odstavené, parkující - ve směru staničení (na komunikaci)"
        else if ($42 == 3)
          $42="vozidlo jedoucí - proti směru staničení (na komunikaci)"
        else if ($42 == 4)
          $42="vozidlo odstavené, parkující - proti směru staničení (na komunikaci)"
        else if ($42 == 5)
          $42="vozidlo jedoucí - na komunikaci bez staničení"
        else if ($42 == 6)
          $42="vozidlo odstavené, parkující - na komunikaci bez staničení"
        else if ($42 == 10 || $42 == 11 || $42 == 12 || $42 == 13 || $42 == 14 || $42 == 15 || $42 == 16 || $42 == 17 || $42 == 18 || $42 == 19 || $42 == 20 || $42 == 21 || $42 == 22 || $42 == 23 || $42 == 24 || $42 == 25 || $42 == 26 || $42 == 27 || $42 == 28 || $42 == 29 || $42 == 30 || $42 == 31 || $42 == 32 || $42 == 33 || $42 == 34 || $42 == 35 || $42 == 36 || $42 == 37 || $42 == 38 || $42 == 39 || $42 == 40 || $42 == 41 || $42 == 42 || $42 == 43 || $42 == 44 || $42 == 45 || $42 == 46 || $42 == 47 || $42 == 48 || $42 == 49 || $42 == 50 || $42 == 51 || $42 == 52 || $42 == 53 || $42 == 54 || $42 == 55 || $42 == 56 || $42 == 57 || $42 == 58 || $42 == 59 || $42 == 60 || $42 == 61 || $42 == 62 || $42 == 63 || $42 == 64 || $42 == 65 || $42 == 66 || $42 == 67 || $42 == 68 || $42 == 69 || $42 == 70 || $42 == 71 || $42 == 72 || $42 == 73 || $42 == 74 || $42 == 75 || $42 == 76 || $42 == 77 || $42 == 78 || $42 == 79 || $42 == 80 || $42 == 81 || $42 == 82 || $42 == 83 || $42 == 84 || $42 == 85 || $42 == 86 || $42 == 87 || $42 == 88 || $42 == 89 || $42 == 90 || $42 == 91 || $42 == 92 || $42 == 93 || $42 == 94 || $42 == 95 || $42 == 96 || $42 == 97 || $42 == 98 || $42 == 99)
          $42="zachycuje postavení vozidla při nehodě na křižovatce"
        else
          $42=""

        # "stav_ridice" column
        if ($44 == 0)
          $44="jiný nepříznivý stav"
        else if ($44 == 1)
          $44="dobrý - žádné nepříznivé okolnosti nebyly zjištěny"
        else if ($44 == 2)
          $44="unaven, usnul, náhlá fyzická indispozice"
        else if ($44 == 3)
          $44="pod vlivem - léků, narkotik"
        else if ($44 == 4)
          $44="pod vlivem - alkoholu, obsah alkoholu v krvi do 0,99 ‰"
        else if ($44 == 5)
          $44="pod vlivem - alkoholu, obsah alkoholu v krvi 1 ‰ a více"
        else if ($44 == 6)
          $44="nemoc, úraz apod."
        else if ($44 == 7)
          $44="invalida"
        else if ($44 == 8)
          $44="řidič při jízdě zemřel (infarkt apod.)"
        else if ($44 == 9)
          $44="pokus o sebevraždu, sebevražda"
        else
          $44=""

        # "vnejsi_ovlivneni_ridice" column
        if ($45 == 0)
          $45="jiné ovlivnění"
        else if ($45 == 1)
          $45="řidič nebyl ovlivněn"
        else if ($45 == 2)
          $45="oslněn sluncem"
        else if ($45 == 3)
          $45="oslněn světlomety jiného vozidla"
        else if ($45 == 4)
          $45="ovlivněn jednáním jiného účastníka silničního provozu"
        else if ($45 == 5)
          $45="ovlivněn při vyhýbání lesní zvěří, domácímu zvířectvu apod."
        else
          $45=""

        # "x" coordinate column, empty value -> empty quotes "" (length 2)
        if (length($48) == 2)
          next

        # "y" coordinate column, empty value -> empty quotes "" (length 2)
        if (length($49) == 2)
          next

        print $1,$4,$5,$6,$7,$8,$64,$16,$11,$12,$13,$18,$19,$20,$22,$24,$25,$26,$27,$28,$29,$30,$31,$2,$32,$33,$36,$37,$38,$42,$44,$45,$48,$49}'"'"' $file | sed  "s/,/./g" >> $ACCIDENTS_CSV_FILE
    fi
done' sh {} +

find "$TEMP_DIR" -type f -name 'CHODCI.csv' -exec bash -c '
for file do
    gawk -F ";" '"'"'
       BEGIN {OFS=";"}
      {
        # "kategorie_chodce" column
        if ($2 == 1)
          $2="muž"
        else if ($2 == 2)
          $2="žena"
        else if ($2 == 3)
          $2="dítě (do 15 let)"
        else if ($2 == 4)
          $2="skupina dětí"
        else if ($2 == 5)
          $2="jiná skupina"
        else
          $2=""

        # "chovani_chodce" column
        if ($4 == 1)
          $4="správné, přiměřené"
        else if ($4 == 2)
          $4="špatný odhad vzdálenosti a rychlosti vozidla"
        else if ($4 == 3)
          $4="náhlé vstoupení do vozovky - z chodníku, krajnice"
        else if ($4 == 4)
          $4="náhlé vstoupení do vozovky - z nástupního nebo dělícího ostrůvku"
        else if ($4 == 5)
          $4="zmatené, zbrklé, nerozhodné jednání"
        else if ($4 == 6)
          $4="náhlá změna směru chůze"
        else if ($4 == 7)
          $4="náraz do vozidla z boku"
        else if ($4 == 8)
          $4="hra dětí na vozovce"
        else
          $4=""

        # "situace_v_miste_nehody" column
        if ($5 == 0)
          $5="jiná situace"
        else if ($5 == 1)
          $5="vstup chodce - na signál VOLNO"
        else if ($5 == 2)
          $5="vstup chodce - na signál STŮJ"
        else if ($5 == 3)
          $5="vstup chodce - do vozovky v blízkosti přechodu (cca do 20 m)"
        else if ($5 == 4)
          $5="přecházení - po vyznačeném přechodu"
        else if ($5 == 5)
          $5="přecházení - těsně před nebo za vozidlem stojícím v zastávce"
        else if ($5 == 6)
          $5="přecházení - těsně před nebo za vozidlem parkujícím"
        else if ($5 == 7)
          $5="chůze - stání na chodníku"
        else if ($5 == 8)
          $5="chůze - po správné straně"
        else if ($5 == 9)
          $5="chůze - po nesprávné straně"
        else if ($5 == 10)
          $5="přecházení - mimo přechod (20 a více metrů od přechodu)"
        else
          $5=""

      print $1,$2,$4,$5}'"'"' $file | sed  "s/,/./g" >> $ACCIDENTS_CHODCI_CSV_FILE
done' sh {} +

join -a 1 -t ';' --nocheck-order $ACCIDENTS_CSV_FILE $ACCIDENTS_CHODCI_CSV_FILE > $ACCIDENTS_JOIN_CSV_FILE
gawk -v ncols="$(echo $COLS | awk -F ";" '{print NF-1}')" -i inplace -F ";" 'BEGIN{OFS=";"}{print(gsub(/;/, ";") == ncols  ? $0 : $0, "", "", "", "")}' $ACCIDENTS_JOIN_CSV_FILE
gawk -v cols="$COLS" -i inplace 'BEGINFILE{print cols}{print}' $ACCIDENTS_JOIN_CSV_FILE
mv $ACCIDENTS_JOIN_CSV_FILE $ACCIDENTS_CSV_FILE

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
