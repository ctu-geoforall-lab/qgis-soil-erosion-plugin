Návod k použití
*******************

Pro vytvoření erozního modelu je nutné vyplnění pěti záložek, ve kterých jsou 
definovány pozemky, na kterých bude výpočet probíhat (EUC), a voleny vstupy 
pro určení faktorů v rovnici USLE (LS, K, C a RP).

EUC
----
Určení erozně uzavřených celků (pozemků), pro které bude určována průměrná 
roční ztráta, probíhá v záložce EUC.

.. figure:: images/euc.png

   Záložka EUC
   
Zde se volí polygonová vektorová vrstva (.shp) definující EUC. Vrstvu je možné 
zvolit ze seznamu vrstev, či ji nahrát přes tlačítko `Nahrát (.shp)`. 
   
Tato vrstva většinou vychází z vrstvy LPIS, ovšem je rovněž možné 
volit svou vlastní vrstvu.

.. warning:: Při zvolení vlastní vrstvy je potřeba dát pozor, aby na většině
             plochy EUC byly definovány faktory K a C.

.. note:: Při využítí vrstvy LPIS je pro správnou funkčnost výpočtu doporučeno 
          zkontrolovat návaznosti polygonů. Zda v místech, kde se jedná o jeden 
          EUC rozdělený mezi několik vlastníků (uživatelů), na sebe polygony 
          navazují (případně se překrývají). (EUC 1A a EUC 1B)
          
          Naopak v místech, kde jsou pozemky erozně odděleny technické protierozním 
          opatření či silnicí, musí být mezi jednotlivými polygony mezera. 
          (EUC 2 a EUC 3)
          
          .. figure:: images/rozdeleni_euc.png
             :width: 75%
             
             Zobrazení EUC se zahrnutými překážkami
         
          Pro základní kontrolu je vhodné využití `ortofota
          <http://geoportal.cuzk.cz/(S(30jees5ocuget4qwpqlemkdv))/Default.aspx?mode=TextMeta&side=wms.verejne&metadataID=CZ-CUZK-WMS-ORTOFOTO-P&metadataXSL=metadata.sluzba&head_tab=sekce-03-gp&menu=3121>`_.

L,S             
----
V záložce L,S se určuje rastr digitálního modelu terénu, nad kterým bude probíhat
výpočet faktorů délky a sklonu svahu (L, S). Vrstvu je možné zvolit ze seznamu
vrstev, či ji nahrát přes tlačítko `Nahrát (rastr)`.

.. figure:: images/ls.png

   Záložka L,S

K
----
V záložce K se volí polygonová vektorová vrstva (.shp) BPEJ, vrstva musí obsahovat pole
s názvem `*BPEJ*` ve formátu 'X.XX.XX', ze kterého se pomocí tlačítka `Vypočítat
K faktor`, vypočte hodnota K a vrstva se dle jeho hodnoty barevně rozliší. 
Případně je možné použít vrstvu s předem vypočteným K faktorem v poli `K`. 
Vrstvu je možné zvolit ze seznamu vrstev, či ji nahrát přes tlačítko `Nahrát (.shp)`.

.. figure:: images/k.png

   Záložka K

.. tip:: Hodnoty K lze poté manuálně upravovat v atributové tabulce (stejně lze 
         upravovat i hodnoty C)
C
----
Záložka C slouží ke zvolení polygonové vektorové vrstvy (.shp) LPIS, vrstva musí obsahovat pole
s názvem `*KULTURAKOD*` s jednoznakovým kódem pro využití pozemku. V rolovací
nabídce se volí primární osevní postup užívaný na pozemcích s ornou půdou. Poté se 
C faktor nastaví kliknutím na tlačítko `Vypočítat C faktor`, přičemž současně
dojde k barevnému rozlišení dle využití pozemku. 

.. figure:: images/c.png

   Záložka C

.. note:: Při využití dat LPIS vyexportovaných z `Registru půd (LPIS)
          <http://eagri.cz/public/app/eagriapp/lpisdata/>`_ a BPEJ z `celostátní 
          databáze
          <http://www.spucr.cz/bpej/celostatni-databaze-bpej>`_, jejich 
          formát odpovídá požadavkům zásuvného modulu.
   
.. tip:: Hodnoty C lze poté manuálně upravovat v atributové tabulce (stejně lze 
         upravovat i hodnoty K)
   
R,P
---
V poslední záložce R,P je možné upravit hodnotu faktoru přívalového deště `R` pro danou oblast, 
tato hodnota je nastavena na 40, průměrná hodnota pro ČR. Dále pak hodnotu
faktoru protierozních opatření `P`, ta je nastavena na 1 (= Nejsou použita žádná
agrotechnická protierozní opatření.)

.. figure:: images/rp.png

   Záložka R,P

Výpočet erozního modelu
------------------------------
Po nastavení všech vstupních hodnot se stisknutím tlačítka provede výpočet 
erozního modelu. Tlačítko je viditelné ze všech záložek. Po spuštění výpočtu 
jsou zobrazovány informace o jeho průběhu pomocí panelu v horní části QGIS.
Z tohoto panelu je také možné výpočet ukončit pomocí tlačítka `Zrušit výpočet`.

.. figure:: images/progressbar.png

   Informačního panel

Erozní model
------------
Po skončení výpočtu se do mapového okna a na první a druhé místo v seznamu 
vrstev přidají vrstvy erozního modelu - `EUC` a `Lokální eroze`. Ukázku těchto
vrstev je možné najít v popisu ukázkového výpočtu.

- Erozní model:
  Vektorová polygonová vrstva `EUC` je vytvořená z vrstvy zadané v záložce `EUC`.
  Do atributové tabulky této vrstvy je přidán nový sloupec `G` s hodnotou průměrné
  roční ztráty půdy pro jednotlivé pozemky, tyto pozemky jsou rovněž obarveny dle
  tabulky ohrožení půdy.

- G faktor:
  Rastrová vrstva zobrazující lokální hodnoty eroze ve stupních šedi.

Při spuštění nového výpočtu se vytvořené vrstvy nahradí novými.


    
