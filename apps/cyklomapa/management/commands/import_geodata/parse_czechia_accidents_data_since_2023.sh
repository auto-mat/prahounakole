#!/usr/bin/env bash

: '
Reclassify Czechia accidents data (CSV files) since 2023
'

CSV_BASE_DIR=$1
export ACCIDENTS_CSV_FILE_BASENAME=$2
EMPTY_VALUE=$3
export CSV_FILE_SEPARATOR=$4

export ACCIDENTS_VEHICLE_CSV_FILE="${CSV_BASE_DIR}/accidents_vehicle.csv"
ACCIDENTS_JOIN_VEHICLE_CSV_FILE="${CSV_BASE_DIR}/accidents_join_vehicle.csv"
export ACCIDENTS_GPS_CSV_FILE="${CSV_BASE_DIR}/accidents_gps.csv"
ACCIDENTS_JOIN_VEHICLE_GPS_CSV_FILE="${CSV_BASE_DIR}/accidents_join_vehicle_gps.csv"
export ACCIDENTS_PEDESTRIANS_CSV_FILE="${CSV_BASE_DIR}/accidents_pedestrians.csv"
ACCIDENTS_JOIN_VEHICLE_GPS_PEDESTRIANS_CSV_FILE="${CSV_BASE_DIR}/accidents_join_gps_vehicle_pedestrians.csv"

# Convert (copy) some UNL file format to the CSV file format
find "$CSV_BASE_DIR" -type f -name '*.unl' -exec bash -c '
for file do
     filename=$(basename -- "$file")
     filename="${filename%.*}"
     dirname=$(dirname "$file")
     csv_file_path="${dirname}/${filename}.csv"
     cp $file $csv_file_path
    sed -i -e "s/|/;/g" -e "s/,/./g" $csv_file_path
done' sh {} +


find "$CSV_BASE_DIR" -type f -regextype posix-extended -regex '.*.[N|n]ehody.csv' -exec bash -c '
for file do
    if [[ 0 ]]; then
       gawk -F $CSV_FILE_SEPARATOR '"'"'
       BEGIN {OFS="'$CSV_FILE_SEPARATOR'"}
      {
        split($2, date2, ".")
        # "druh_pozemni_komunikace" p36 column
        if ($35 == 0)
          $35="dálnice"
        else if ($35 == 1)
          $35="silnice 1. třídy"
        else if ($35 == 2)
          $35="silnice 2. třídy"
        else if ($35 == 3)
          $35="silnice 3. třídy"
        else if ($35 == 4)
          $35="uzel - tj. křižovatka sledovaná ve vybraných městech"
        else if ($35 == 5)
          $35="komunikace sledovaná - (ve vybraných městech)"
        else if ($35 == 6)
          $35="komunikace místní"
        else if ($35 == 7)
          $35="komunikace účelová - polní a lesní cesty atd."
        else if ($35 == 8)
          $35="komunikace účelová - ostatní (parkoviště, odpočívky apod.)"
        else
          $35=""

        # "datum" p2a column
        $2 = strftime("%Y-%m-%d", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0"))

        # "cas" p2b column
        if ($3 == "\"2560\"")
          $3=""
        else if (length($3) == 6)
          $3=substr($3, 2, 2)":"substr($3, 4, 2)
        else
          $3=substr($3, 2, 1)":"substr($3, 3, 2)

        # "den" calculated column
        if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 1)
          $5="Po"
        else if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 2)
          $5="Ut"
        else if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 3)
          $5="St"
        else if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 4)
          $5="Čt"
        else if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 5)
          $5="Pa"
        else if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 6)
          $5="So"
        else if (strftime("%u", mktime(date2[3]" "date2[2]" "date2[1] " 0 0 0")) == 7)
          $5="Ne"
        else
          $5=""

        # "druh" p6 column
        if ($8 == 0)
          $8="jiný druh nehody"
        if ($8 == 1)
          $8="srážka s jedoucím nekolejovým vozidlem"
        else if ($8 == 2)
          $8="srážka s vozidlem zaparkovaným, odstaveným"
        else if ($8 == 3)
          $8="srážka s pevnou překážkou"
        else if ($8 == 4)
          $8="srážka s chodcem"
        else if ($8 == 5)
          $8="s lesní zvěří"
        else if ($8 == 6)
          $8="s domácím zvířetem"
        else if ($8 == 7)
          $8="s vlakem"
        else if ($8 == 8)
          $8="s tramvají"
        else if ($8 == 9)
          $8="havárie"
        else
          $8=""

        # "druh_srazky_jedoucich_vozidel" p7 column
        if ($9 == 0)
          $9="nepřichází v úvahu (nejedná se o srážku jedoucích vozidel)"
        else if ($9 == 1)
          $9="čelní"
        else if ($9 == 2)
          $9="boční"
        else if ($9 == 3)
          $9="z boku"
        else if ($9 == 4)
          $9="zezadu"
        else
          $9=""

        # "lokalita" p5a column
        if ($7 == 1)
          $7="v obci"
        else if ($7 == 2)
          $7="mimo obec"
        else
          $7=""

        # "nasledky" p13 column
        # p13a
        if ($17 > 0)
          $17="usmrceno osob"
        # p13b
        else if ($18 > 0)
          $17="těžce zraněno osob"
        # p13c
        else if ($19 > 0)
          $17="lehce zraněno osob"
        else if ($17 == 0 || $18 == 0 || $19 == 0)
          $17="bez zranění osob"
        else
          $17=""

        # "zavineni" p10 column
        if ($13 == 0)
          $13="jiné zavinění"
        else if ($13 == 1)
          $13="řidičem motorového vozidla"
        else if ($13 == 2)
          $13="řidičem nemotorového vozidla"
        else if ($13 == 3)
          $13="chodcem"
        else if ($13 == 4)
          $13="lesní zvěří, domácím zvířectvem"
        else if ($13 == 5)
          $13="jiným účastníkem silničního provozu"
        else if ($13 == 6)
          $13="závadou komunikace"
        else if ($13 == 7)
          $13="technickou závadou vozidla"
        else
          $13=""

        # "alkohol_u_vinika_nehody_pritomen" p11 column
        if ($14 == 0)
          $14="nezjišťováno"
        else if ($14 == 1)
          $14="ano (obsah alkoholu v krvi do 0,24 ‰)"
        else if ($14 == 2)
          $14="ne"
        else if ($14 == 3)
          $14="ano (obsah alkoholu v krvi od 0,24 ‰ do 0,5 ‰)"
        else if ($14 == 4)
          $14="pod vlivem drog"
        else if ($14 == 5)
          $14="pod vlivem alkoholu a drog"
        else if ($14 == 6)
          $14="ano (obsah alkoholu v krvi od 0,5 ‰ do 0,8 ‰)"
        else if ($14 == 7)
          $14="ano (obsah alkoholu v krvi od 0,8 ‰ do 1,0 ‰)"
        else if ($14 == 8)
          $14="ano (obsah alkoholu v krvi od 1,0 ‰ do 1,5 ‰)"
        else if ($14 == 9)
          $14="ano (obsah alkoholu v krvi 1,5 ‰ a více)"
        else
          $14=""

        # "priciny" p12 column
        if ($16 == 100)
          $16="nezaviněná řidičem"
        else if ($16 == 201)
          $16="nepřizpůsobení rychlosti - intenzitě (hustotě) provozu"
        else if ($16 == 202)
          $16="nepřizpůsobení rychlosti - viditelnosti (mlha, soumrak, jízda v noci na tlumená světla apod.)"
        else if ($16 == 203)
          $16="nepřizpůsobení rychlosti - vlastnostem vozidla a nákladu"
        else if ($16 == 204)
          $16="nepřizpůsobení rychlosti - stavu vozovky (náledí, výtluky, bláto, mokrý povrch apod.)"
        else if ($16 == 205)
          $16="nepřizpůsobení rychlosti - dopravně technickému stavu vozovky (zatáčka, klesání, stoupání, šířka vozovky apod.)"
        else if ($16 == 206)
          $16="překročení předepsané rychlosti stanovené pravidly"
        else if ($16 == 207)
          $16="překročení rychlosti stanovené dopravní značkou"
        else if ($16 == 208)
          $16="nepřizpůsobení rychlosti - bočnímu, nárazovému větru (i při míjení, předjíždění vozidel)"
        else if ($16 == 209)
          $16="jiný druh nepřiměřené rychlosti"
        else if ($16 == 301)
          $16="předjíždění - vpravo"
        else if ($16 == 302)
          $16="předjíždění - bez dostatečného bočního odstupu"
        else if ($16 == 303)
          $16="předjíždění - bez dostatečného rozhledu (v nepřehledné zatáčce nebo její blízkosti, před vrcholem stoupání apod.)"
        else if ($16 == 304)
          $16="předjíždění - došlo k ohrožení protijedoucího řidiče vozidla (špatný odhad vzdálenosti potřebné k předjetí apod.)"
        else if ($16 == 305)
          $16="předjíždění - došlo k ohrožení předjížděného řidiče vozidla (vynucené zařazení, předjížděný řidič musel prudce brzdit, měnit směr jízdy apod.)"
        else if ($16 == 306)
          $16="předjíždění - vlevo vozidla odbočujícího vlevo"
        else if ($16 == 307)
          $16="předjíždění - v místech, kde je to zakázáno dopravní značkou"
        else if ($16 == 308)
          $16="předjíždění - byla přejeta podélná čára souvislá"
        else if ($16 == 309)
          $16="bránění v předjíždění"
        else if ($16 == 310)
          $16="přehlédnutí již předjíždějícícho souběžně jedoucího vozidla"
        else if ($16 == 311)
          $16="jiný druh nesprávného předjíždění"
        else if ($16 == 401)
          $16="jízda na červenou 3-barevného semaforu"
        else if ($16 == 402)
          $16="proti příkazu dopravní značky - stůj dej přednost"
        else if ($16 == 403)
          $16="proti příkazu dopravní značky - dej přednost"
        else if ($16 == 404)
          $16="vozidlu přijíždějícímu zprava"
        else if ($16 == 405)
          $16="při odbočování vlevo"
        else if ($16 == 406)
          $16="tramvají, která odbočuje"
        else if ($16 == 407)
          $16="protijedoucímu vozidlu při objíždění překážky"
        else if ($16 == 408)
          $16="při zařazování do proudu jedoucích vozidel ze stanice, místa zastavení nebo stání"
        else if ($16 == 409)
          $16="při vjíždění na silnici"
        else if ($16 == 410)
          $16="při otáčení nebo couvání"
        else if ($16 == 411)
          $16="při přejíždění z jednoho jízdního pruhu do druhého"
        else if ($16 == 412)
          $16="chodci na vyznačeném přechodu"
        else if ($16 == 413)
          $16="při odbočování vlevo - souběžně jedoucímu vozidlu"
        else if ($16 == 414)
          $16="jiné nedání přednosti"
        else if ($16 == 501)
          $16="jízda po nesprávné straně vozovky, vjetí do protisměru"
        else if ($16 == 502)
          $16="vyhýbání bez dostatečného bočního odstupu (vůle)"
        else if ($16 == 503)
          $16="nedodržení bezpečné vzdálenosti za vozidlem"
        else if ($16 == 504)
          $16="nesprávné otáčení nebo couvání"
        else if ($16 == 505)
          $16="chyby při udání směru jízdy"
        else if ($16 == 506)
          $16="bezohledná, agresivní, neohleduplná jízda"
        else if ($16 == 507)
          $16="náhlé bezdůvodné snížení rychlosti jízdy, zabrzdění nebo zastavení"
        else if ($16 == 508)
          $16="řidič se plně nevěnoval řízení vozidla"
        else if ($16 == 509)
          $16="samovolné rozjetí nezajištěného vozidla"
        else if ($16 == 510)
          $16="vjetí na nezpevněnou komunikaci"
        else if ($16 == 511)
          $16="nezvládnutí řízení vozidla"
        else if ($16 == 512)
          $16="jízda (vjetí) jednosměrnou ulicí, silnicí (v protisměru)"
        else if ($16 == 513)
          $16="nehoda v důsledku použití (policií) prostředků k násilnému zastavení vozidla (zastavovací pásy, zábrana, vozidlo atp.)"
        else if ($16 == 514)
          $16="nehoda v důsledku použití služební zbraně (policií)"
        else if ($16 == 515)
          $16="nehoda při provádění služebního zákroku (pronásledování pachatele atd.)"
        else if ($16 == 516)
          $16="jiný druh nesprávného způsobu jízdy"
        else if ($16 == 601)
          $16="závada řízení"
        else if ($16 == 602)
          $16="závada provozní brzdy"
        else if ($16 == 603)
          $16="neúčinná nebo nefungující parkovací brzda"
        else if ($16 == 604)
          $16="opotřebení běhounu pláště pod stanovenou mez"
        else if ($16 == 605)
          $16="defekt pneumatiky způsobený průrazem nebo náhlým únikem vzduchu"
        else if ($16 == 606)
          $16="závada osvětlovací soustavy vozidla (neúčinná, chybějící, znečištěná apod.)"
        else if ($16 == 607)
          $16="nepřipojená nebo poškozená spojovací hadice pro bzrdění přípojného vozidla"
        else if ($16 == 608)
          $16="nesprávné uložení nákladu"
        else if ($16 == 609)
          $16="upadnutí, ztráta kola vozidla (i rezervního)"
        else if ($16 == 610)
          $16="zablokování kol v důsledku mechanické závady vozidla (zadřený motor, převodovka, rozvodovka, spadlý řetěz apod.)"
        else if ($16 == 611)
          $16="lom závěsu kola, pružiny"
        else if ($16 == 612)
          $16="nezajištěná nebo poškozená bočnice (i u přívěsu)"
        else if ($16 == 613)
          $16="závada závěsu pro přívěs"
        else if ($16 == 614)
          $16="utržená spojovací hřídel"
        else if ($16 == 615)
          $16="jiná technická závada (vztahuje se i na přípojná vozidla)"
        else
          $16=""

        # "druh_povrchu_vozovky" p15 column
        if ($21 == 1)
          $21="dlažba"
        else if ($21 == 2)
          $21="živice"
        else if ($21 == 3)
          $21="beton"
        else if ($21 == 4)
          $21="panely"
        else if ($21 == 5)
          $21="štěrk"
        else if ($21 == 6)
          $21="jiný nezpevněný povrch"
        else
          $21=""

        # "stav_povrchu_vozovky_v_dobe_nehody" p16 column
        if ($22 == 0)
          $22="jiný stav povrchu vozovky v době nehody"
        else if ($22 == 1)
          $22="povrch suchý - neznečištěný"
        else if ($22 == 2)
          $22="povrch suchý - znečištěný (písek, prach, listí, štěrk atd.)"
        else if ($22 == 3)
          $22="povrch mokrý"
        else if ($22 == 4)
          $22="na vozovce je bláto"
        else if ($22 == 5)
          $22="na vozovce je náledí, ujetý sníh - posypané"
        else if ($22 == 6)
          $22="na vozovce je náledí, ujetý sníh - neposypané"
        else if ($22 == 7)
          $22="na vozovce je rozlitý olej, nafta apod."
        else if ($22 == 8)
          $22="souvislá sněhová vrstva, rozbředlý sníh"
        else if ($22 == 9)
          $22="náhlá změna stavu vozovky (námraza na mostu, místní náledí)"
        else
          $22=""

        # "stav_komunikace" p17 column
        if ($23 == 1)
          $23="dobrý, bez závad"
        else if ($23 == 2)
          $23="podélný sklon vyšší než 8 %"
        else if ($23 == 3)
          $23="nesprávně umístěná, znečištěná, chybějící dopravní značka"
        else if ($23 == 4)
          $23="zvlněný povrch v podélném směru"
        else if ($23 == 5)
          $23="souvislé výtluky"
        else if ($23 == 6)
          $23="nesouvislé výtluky"
        else if ($23 == 7)
          $23="trvalé zúžení vozovky"
        else if ($23 == 8)
          $23="příčná stružka, hrbol, vystouplé, propadlé kolejnice"
        else if ($23 == 9)
          $23="neoznačená nebo nedostatečně označená překážka na komunikaci"
        else if ($23 == 10)
          $23="přechodná uzavírka jednoho jízdního pruhu"
        else if ($23 == 11)
          $23="přechodná uzavírka komunikace nebo jízdního pásu"
        else if ($23 == 12)
          $23="jiný (neuvedený) stav nebo závada komunikace"
        else
          $23=""

        # "viditelnost" p19 column
        if ($25 == 1)
          $25="ve dne - viditelnost nezhoršená vlivem povětrnostních podmínek"
        else if ($25 == 2)
          $25="ve dne - zhoršená viditelnost (svítání, soumrak)"
        else if ($25 == 3)
          $25="ve dne - zhoršená viditelnost vlivem povětrnostních podmínek (mlha, sněžení, déšť apod.)"
        else if ($25 == 4)
          $25="v noci - s veřejným osvětlením, viditelnost nezhoršená vlivem povětrnostních podmínek"
        else if ($25 == 5)
          $25="v noci - s veřejným osvětlením, zhoršená viditelnost vlivem povětrnostních podmínek (mlha, déšť, sněžení apod.)"
        else if ($25 == 6)
          $25="v noci - bez veřejného osvětlení, viditelnost nezhoršená vlivem povětrnostních podmínek"
        else if ($25 == 7)
          $25="v noci - bez veřejného osvětlení, viditelnost zhoršená vlivem povětrnostních podmínek (mlha, déšť, sněžení apod.)"
        else
          $25=""

        # "deleni_komunikace" p21 column
        if ($27 == 0)
          $27="žádná z uvedených"
        else if ($27 == 1)
          $27="dvoupruhová"
        else if ($27 == 2)
          $27="třípruhová"
        else if ($27 == 3)
          $27="čtyřpruhová s dělícím pásem"
        else if ($27 == 4)
          $27="čtyřpruhová s dělící čarou"
        else if ($27 == 5)
          $27="vícepruhová"
        else if ($27 == 6)
          $27="rychlostní komunikace"
        else
          $27=""

        # "situovani_nehody_na_komunikaci" p22 column
        if ($28 == 0)
          $28="žádné z uvedených"
        else if ($28 == 1)
          $28="na jízdním pruhu"
        else if ($28 == 2)
          $28="na odstavném pruhu"
        else if ($28 == 3)
          $28="na krajnici"
        else if ($28 == 4)
          $28="na odbočovacím, připojovacím pruhu"
        else if ($28 == 5)
          $28="na pruhu pro pomalá vozidla"
        else if ($28 == 6)
          $28="na chodníku nebo ostrůvku"
        else if ($28 == 7)
          $28="na kolejích tramvaje"
        else if ($28 == 8)
          $28="mimo komunikaci"
        else if ($28 == 9)
          $28="na stezce pro cyklisty"
        else
          $28=""

        # "rizeni_provozu_v_dobe_nehody" p23 column
        if ($29 == 0)
          $29="žádný způsob řízení provozu"
        else if ($29 == 1)
          $29="policistou nebo jiným pověřeným orgánem"
        else if ($29 == 2)
          $29="světelným signalizačním zařízením"
        else if ($29 == 3)
          $29="místní úprava (vyplní se místní úprava přednosti v jízdě)"
        else
          $29=""

        # "mistni_uprava_prednosti_v_jizde" p24 column
        if ($30 == 0)
          $30="žádná místní úprava"
        else if ($30 == 1)
          $30="světelná signalilzace přepnuta na přerušovanou žlutou"
        else if ($30 == 2)
          $30="světelná signalizace mimo provoz"
        else if ($30 == 3)
          $30="přednost vyznačena dopravními značkami"
        else if ($30 == 4)
          $30="přednost vyznačena přenosnými dopravními značkami nebo zařízením"
        else if ($30 == 5)
          $30="přednost nevyznačena - vyplývá z pravidel silníčního provozu"
        else
          $30=""

        # "specificka_mista_a_objekty_v_miste_nehody" p27 column
        if ($31 == 0)
          $31="žádné nebo žádné z uvedených"
        else if ($31 == 1)
          $31="přechod pro chodce"
        else if ($31 == 2)
          $31="v blízkosti přechodu pro chodce (do vzdálenosti 20 m)"
        else if ($31 == 3)
          $31="železniční přejezd nezabezpečený závorami ani světelným výstražným zařízením"
        else if ($31 == 4)
          $31="železniční přejezd zabezpečený"
        else if ($31 == 5)
          $31="most, nadjezd, podjezd, tunel"
        else if ($31 == 6)
          $31="zastávka autobusu, trolejbusu, tramvaje s nástup. ostrůvkem"
        else if ($31 == 7)
          $31="zastávka tramvaje, autobusu, trolejbusu bez nástup. ostrůvku"
        else if ($31 == 8)
          $31="výjezd z parkoviště, lesní cesty apod. (pol. 36 = 7,8)"
        else if ($31 == 9)
          $31="čerpadlo pohonných hmot"
        else if ($31 == 10)
          $31="parkoviště přiléhající ke komunikaci"
        else
          $31=""

        # "smerove_pomery" p28 column
        if ($32 == 1)
          $32="přímý úsek"
        else if ($32 == 2)
          $32="přímý úsek po projetí zatáčkou (do vzdálenosti cca 100 m od optického konce zatáčky)"
        else if ($32 == 3)
          $32="zatáčka"
        else if ($32 == 4)
          $32="křižovatka průsečná - čtyřramenná"
        else if ($32 == 5)
          $32="křižovatka styková - tříramenná"
        else if ($32 == 6)
          $32="křižovatka pěti a víceramenná"
        else if ($32 == 7)
          $32="kruhový objezd"
        else
          $32=""

        # "misto_dopravni_nehody" p35 column
        if ($34 == 00)
          $34="mimo křižovatku"
        else if ($34 == 10)
          $34="na kžižovatce - jedná-li se o křížení místních komunikací, účelových komunikací nebo jde o mezilehlou křižovatku (na sledovaném úseku ve sledovaných městech)"
        else if ($34 == 11 || $34 == 12 || $34 == 13 || $34 == 14 || $34 == 15 || $34 == 16 || $34 == 17 || $34 == 18)
          $34="uvnitř zóny 1-8 předmětné křižovatky"
        else if ($34 == 19)
          $34="na křižovatce - uvnitř hranic křižovatky definovaných pro systém evidence nehod (zóna 9)"
        else if ($34 == 22 || $34 == 23 || $34 == 24 || $34 == 25 || $34 == 26 || $34 == 27 || $34 == 28)
          $34="na vjezdové nebo výjezdové části větve při mimoúrovňovém křížení"
        else if ($34 == 29)
          $34="mimo zónu - uvnitř zóny 1-8 předmětné křižovatky, na křižovatce - uvnitř hranic křižovatky definovaných pro systém evidence nehod (zóna 9) a na vjezdové nebo výjezdové části větve při mimoúrovňovém křížení"
        else
          $34=""

        # "druh_krizujici_komunikace" p39 column
        if ($38 == 1)
          $38="silnice 1. třídy"
        else if ($38 == 2)
          $38="silnice 2. třídy"
        else if ($38 == 3)
          $38="silnice 3. třídy"
        else if ($38 == 6)
          $38="místní komunikace"
        else if ($38 == 7)
          $38="účelová komunikace"
        else if ($38 == 9)
          $38="větev mimoúrovňové křižovatky"
        else
          $38=""

        # "pocet_zucastnenych_vozidel" p34 column

        print $1,$2,$5,$3,$8,$9,$7,$17,$13,$14,$16,$21,$22,$23,$25,$27,$28,$29,$30,$31,$32,$33,$34,$35,$38}'"'"' $file | sed  "s/,/./g" | sort -t $CSV_FILE_SEPARATOR -k 1,1 > $ACCIDENTS_CSV_FILE_BASENAME
    fi
done' sh {} +


find "$CSV_BASE_DIR" -type f  -regextype posix-extended -regex '.*.[V|v]ozidla.csv' -exec bash -c '
for file do
    gawk -F $CSV_FILE_SEPARATOR '"'"'
       BEGIN {OFS="'$CSV_FILE_SEPARATOR'"}
      {
        # "druh_vozidla" p44 column
        if ($3 == 0 || $3 == 00)
          $3="moped"
        else if ($3 == 1)
          $3="malý motocykl (do 50 ccm)"
        else if ($3 == 2)
          $3="motocykl (včetně sidecarů, skútrů apod.)"
        else if ($3 == 3)
          $3="osobní automobil bez přívěsu"
        else if ($3 == 4)
          $3="osobní automobil s přívěsem"
        else if ($3 == 5)
          $3="nákladní automobil (včetně multikáry, autojeřábu, cisterny atd.)"
        else if ($3 == 6)
          $3="nákladní automobil s přívěsem"
        else if ($3 == 7)
          $3="nákladní automobil s návěsem"
        else if ($3 == 8)
          $3="autobus"
        else if ($3 == 9)
          $3="traktor (i s přívěsem)"
        else if ($3 == 10)
          $3="tramvaj"
        else if ($3 == 11)
          $3="trolejbus"
        else if ($3 == 12)
          $3="jiné motorové vozidlo (zemědělské, lesní, stavební stroje atd.)"
        else if ($3 == 13)
          $3="jízdní kolo"
        else if ($3 == 14)
          $3="povoz, jízda na koni"
        else if ($3 == 15)
          $3="jiné nemotorové vozidlo"
        else if ($3 == 16)
          $3="vlak"
        else if ($3 == 17)
          $3="nezjištěno, řidič ujel"
        else if ($3 == 18)
          $3="jiný druh vozidla"
        else
          $3=""

        # "charakteristika_vozidla" p48a column
        if ($9 == 00)
          $9="nezjištěno"
        else if ($9 == 1)
          $9="soukromé - nevyužívané k výdělečné činnost"
        else if ($9 == 2)
          $9="soukromé - využívané k výdělečné činnosti"
        else if ($9 == 3)
          $9="soukromá organizace - (podnikatel, s.r.o., v.o.s., a.s., atd.)"
        else if ($9 == 4)
          $9="veřejná hromadná doprava"
        else if ($9 == 5)
          $9="městská hromadná doprava"
        else if ($9 == 6)
          $9="mezinárodní kamionová doprava"
        else if ($9 == 7)
          $9="TAXI"
        else if ($9 == 8)
          $9="státní podnik, státní organizace"
        else if ($9 == 9)
          $9="registrované mimo území ČR"
        else if ($9 == 10)
          $9="zastupitelský úřad"
        else if ($9 == 11)
          $9="ministerstvo vnitra"
        else if ($9 == 12)
          $9="policie ČR"
        else if ($9 == 13)
          $9="městská, obecní policie"
        else if ($9 == 14)
          $9="soukromé bezpečnostní agentury"
        else if ($9 == 15)
          $9="ministerstvo obrany"
        else if ($9 == 16)
          $9="jiné"
        else if ($9 == 17)
          $9="odcizené"
        else if ($9 == 18)
          $9="vozidlo AUTOŠKOLY provádějící výcvik"
        else
          $9=""

        # "smyk" p49 column
        if ($11 == 0)
          $11="ne"
        else if ($11 == 1)
          $11="ano"
        else
          $11=""

        # "vozidlo_po_nehode" p50a column
        if ($12 == 0)
          $12="žádná z uvedených"
        else if ($12 == 1)
          $12="nedošlo k požáru"
        else if ($12 == 2)
          $12="došlo k požáru"
        else if ($12 == 3)
          $12="řidič ujel - zjištěn"
        else if ($12 == 4)
          $12="řidič ujel (utekl) - nezjištěn"
        else
          $12=""

        # "smer_jizdy_nebo_postaveni_vozidla" p52 column
        if ($15 == 1)
          $15="vozidlo jedoucí - ve měru staničení (na komunikaci)"
        else if ($15 == 2)
          $15="vozidlo odstavené, parkující - ve směru staničení (na komunikaci)"
        else if ($15 == 3)
          $15="vozidlo jedoucí - proti směru staničení (na komunikaci)"
        else if ($15 == 4)
          $15="vozidlo odstavené, parkující - proti směru staničení (na komunikaci)"
        else if ($15 == 5)
          $15="vozidlo jedoucí - na komunikaci bez staničení"
        else if ($15 == 6)
          $15="vozidlo odstavené, parkující - na komunikaci bez staničení"
        else if ($15 == 10 || $15 == 11 || $15 == 12 || $15 == 13 || $15 == 14 || $15 == 15 || $15 == 16 || $15 == 17 || $15 == 18 || $15 == 19 || $15 == 20 || $15 == 21 || $15 == 22 || $15 == 23 || $15 == 24 || $15 == 25 || $15 == 26 || $15 == 27 || $15 == 28 || $15 == 29 || $15 == 30 || $15 == 31 || $15 == 32 || $15 == 33 || $15 == 34 || $15 == 35 || $15 == 36 || $15 == 37 || $15 == 38 || $15 == 39 || $15 == 40 || $15 == 41 || $15 == 42 || $15 == 43 || $15 == 44 || $15 == 45 || $15 == 46 || $15 == 47 || $15 == 48 || $15 == 49 || $15 == 50 || $15 == 51 || $15 == 52 || $15 == 53 || $15 == 54 || $15 == 55 || $15 == 56 || $15 == 57 || $15 == 58 || $15 == 59 || $15 == 60 || $15 == 61 || $15 == 62 || $15 == 63 || $15 == 64 || $15 == 65 || $15 == 66 || $15 == 67 || $15 == 68 || $15 == 69 || $15 == 70 || $15 == 71 || $15 == 72 || $15 == 73 || $15 == 74 || $15 == 75 || $15 == 76 || $15 == 77 || $15 == 78 || $15 == 79 || $15 == 80 || $15 == 81 || $15 == 82 || $15 == 83 || $15 == 84 || $15 == 85 || $15 == 86 || $15 == 87 || $15 == 88 || $15 == 89 || $15 == 90 || $15 == 91 || $15 == 92 || $15 == 93 || $15 == 94 || $15 == 95 || $15 == 96 || $15 == 97 || $15 == 98 || $15 == 99)
          $15="zachycuje postavení vozidla při nehodě na křižovatce"
        else
          $15=""

        # "stav_ridice" p57 column
        if ($20 == 0)
          $20="jiný nepříznivý stav"
        else if ($20 == 1)
          $20="dobrý - žádné nepříznivé okolnosti nebyly zjištěny"
        else if ($20 == 2)
          $20="unaven, usnul, náhlá fyzická indispozice"
        else if ($20 == 3)
          $20="pod vlivem - léků, narkotik"
        else if ($20 == 4)
          $20="pod vlivem - alkoholu, obsah alkoholu v krvi do 0,99 ‰"
        else if ($20 == 5)
          $20="pod vlivem - alkoholu, obsah alkoholu v krvi 1 ‰ a více"
        else if ($20 == 6)
          $20="nemoc, úraz apod."
        else if ($20 == 7)
          $20="invalida"
        else if ($20 == 8)
          $20="řidič při jízdě zemřel (infarkt apod.)"
        else if ($20 == 9)
          $20="pokus o sebevraždu, sebevražda"
        else
          $20=""

        # "vnejsi_ovlivneni_ridice" p58 column
        if ($21 == 0)
          $21="jiné ovlivnění"
        else if ($21 == 1)
          $21="řidič nebyl ovlivněn"
        else if ($21 == 2)
          $21="oslněn sluncem"
        else if ($21 == 3)
          $21="oslněn světlomety jiného vozidla"
        else if ($21 == 4)
          $21="ovlivněn jednáním jiného účastníka silničního provozu"
        else if ($21 == 5)
          $21="ovlivněn při vyhýbání lesní zvěří, domácímu zvířectvu apod."
        else
          $21=""

      print $1,$3,$9,$11,$12,$15,$20,$21}'"'"' $file | sort -t $CSV_FILE_SEPARATOR -k 1,1 > $ACCIDENTS_VEHICLE_CSV_FILE
done' sh {} +

if [ -f $ACCIDENTS_CSV_FILE_BASENAME ] && [ -f $ACCIDENTS_VEHICLE_CSV_FILE ]; then
    join -a 1 -t $CSV_FILE_SEPARATOR -e $EMPTY_VALUE -o 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 1.10 1.11 1.12 1.13 1.14 1.15 1.16 1.17 1.18 1.19 1.20 1.21 1.22 1.23 1.24 1.25 2.2 2.3 2.4 2.5 2.6 2.7 2.8 --nocheck-order $ACCIDENTS_CSV_FILE_BASENAME $ACCIDENTS_VEHICLE_CSV_FILE > $ACCIDENTS_JOIN_VEHICLE_CSV_FILE
fi

find "$CSV_BASE_DIR" -type f -type f -regextype posix-extended -regex '.*.(GPS|gps).csv' -exec bash -c '
for file do
    gawk -F $CSV_FILE_SEPARATOR '"'"'
       BEGIN {OFS="'$CSV_FILE_SEPARATOR'"}
      {
        # "x" e coordinate e column, empty value -> empty quotes "" (length 2)
        if (length($2) == 2)
          next

        # "y" coordinate e column, empty value -> empty quotes "" (length 2)
        if (length($3) == 2)
          next

      print $1,$2,$3}'"'"' $file | sed  "s/,/./g" | sort -t $CSV_FILE_SEPARATOR -k 1,1 > $ACCIDENTS_GPS_CSV_FILE
done' sh {} +

if [ -f $ACCIDENTS_JOIN_VEHICLE_CSV_FILE ] && [ -f $ACCIDENTS_GPS_CSV_FILE ]; then
    join -a 1 -t ';' -e $CSV_FILE_SEPARATOR -o 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 1.10 1.11 1.12 1.13 1.14 1.15 1.16 1.17 1.18 1.19 1.20 1.21 1.22 1.23 1.24 1.25 1.26 1.27 1.28 1.29 1.30 1.31 1.32 2.2 2.3 --nocheck-order $ACCIDENTS_JOIN_VEHICLE_CSV_FILE $ACCIDENTS_GPS_CSV_FILE > $ACCIDENTS_JOIN_VEHICLE_GPS_CSV_FILE
fi

find "$CSV_BASE_DIR" -type f -regex '.*.[C|c]hodci.csv' -exec bash -c '
for file do
    gawk -F $CSV_FILE_SEPARATOR '"'"'
       BEGIN {OFS="'$CSV_FILE_SEPARATOR'"}
      {
        # "kategorie_chodce" p29 column
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

        # "chovani_chodce" p31 column
        if ($8 == 1)
          $8="správné, přiměřené"
        else if ($8 == 2)
          $8="špatný odhad vzdálenosti a rychlosti vozidla"
        else if ($8 == 3)
          $8="náhlé vstoupení do vozovky - z chodníku, krajnice"
        else if ($8 == 4)
          $8="náhlé vstoupení do vozovky - z nástupního nebo dělícího ostrůvku"
        else if ($8 == 5)
          $8="zmatené, zbrklé, nerozhodné jednání"
        else if ($8 == 6)
          $8="náhlá změna směru chůze"
        else if ($8 == 7)
          $8="náraz do vozidla z boku"
        else if ($8 == 8)
          $8="hra dětí na vozovce"
        else
          $8=""

        # "situace_v_miste_nehody" p32 column
        if ($9 == 0)
          $9="jiná situace"
        else if ($9 == 1)
          $9="vstup chodce - na signál VOLNO"
        else if ($9 == 2)
          $9="vstup chodce - na signál STŮJ"
        else if ($9 == 3)
          $9="vstup chodce - do vozovky v blízkosti přechodu (cca do 20 m)"
        else if ($9 == 4)
          $9="přecházení - po vyznačeném přechodu"
        else if ($9 == 5)
          $9="přecházení - těsně před nebo za vozidlem stojícím v zastávce"
        else if ($9 == 6)
          $9="přecházení - těsně před nebo za vozidlem parkujícím"
        else if ($9 == 7)
          $9="chůze - stání na chodníku"
        else if ($9 == 8)
          $9="chůze - po správné straně"
        else if ($9 == 9)
          $9="chůze - po nesprávné straně"
        else if ($9 == 10)
          $9="přecházení - mimo přechod (20 a více metrů od přechodu)"
        else
          $9=""

      print $1,$2,$8,$9}'"'"' $file | sort -t $CSV_FILE_SEPARATOR -k 1,1  > $ACCIDENTS_PEDESTRIANS_CSV_FILE
done' sh {} +

set -e
EXIT_CODE=0

if [ -f $ACCIDENTS_JOIN_VEHICLE_GPS_CSV_FILE ] && [ -f $ACCIDENTS_PEDESTRIANS_CSV_FILE ]; then
    join -a 1 -t $CSV_FILE_SEPARATOR -e $EMPTY_VALUE -o 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 1.10 1.11 1.12 1.13 1.14 1.15 1.16 1.17 1.18 1.19 1.20 1.21 1.22 1.23 1.24 1.25 1.26 1.27 1.28 1.29 1.30 1.31 1.32 1.33 1.34 2.2 2.3 2.4 --nocheck-order $ACCIDENTS_JOIN_VEHICLE_GPS_CSV_FILE $ACCIDENTS_PEDESTRIANS_CSV_FILE > $ACCIDENTS_JOIN_VEHICLE_GPS_PEDESTRIANS_CSV_FILE || EXIT_CODE=$?
    if [ $EXIT_CODE == 0 ]; then
        mv $ACCIDENTS_JOIN_VEHICLE_GPS_PEDESTRIANS_CSV_FILE $ACCIDENTS_CSV_FILE_BASENAME
    else
	      mv $ACCIDENTS_JOIN_VEHICLE_GPS_CSV_FILE $ACCIDENTS_CSV_FILE_BASENAME
    fi
fi
