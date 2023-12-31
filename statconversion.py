import json
import os
import re
import csv
from rdflib import Graph, URIRef, Literal

datanamespace="http://archaeolink.github.io/hgis_rdf/"

sources={
"1":{"label":"Amtliche Zahl","uri":"http://www.wikidata.org/entity/Q29509043"},
"2":{"label":"Amtliche Berechnung oder Schätzung","uri":"http://www.wikidata.org/entity/Q29509043"},
"3":{"label":"Nichtamtliche Berechnung oder Schätzung (zeitgenössisch)","uri":"http://www.wikidata.org/entity/Q29509080"},
"4":{"label":"Interpolierte oder sonstig errechnete Zahl (neuere Literatur)","uri":"http://www.wikidata.org/entity/Q60070514"},
"5":{"label":"Interpolierte oder sonstig errechnete Zahl (HGIS Germany)","uri":"http://www.wikidata.org/entity/Q60070514"},
"6":{"label":"Fortgeschriebene Zahl (HGIS Germany)","uri":"http://www.wikidata.org/entity/Q60070514"},
"7":{"label":"Geschätzte Zahl (HGIS Germany)","uri":"http://www.wikidata.org/entity/Q60070514"}
}

stringToShorthand={
"Aachen":{"label":"ACH","uri":"http://www.wikidata.org/entity/Q896929"},
"Anhalt-Dessau-Köthen":{"label":"ADK","uri":"http://www.wikidata.org/entity/Q2944524"},
"Allenstein":{"label":"ALL","uri":"http://www.wikidata.org/entity/Q82765"},
"Anhalt-Bernburg":{"label":"ANB","uri":"http://www.wikidata.org/entity/Q686965"},
"Anhalt-Köthen":{"label":"ANK","uri":"http://www.wikidata.org/entity/Q264970"},
"Arnsberg":{"label":"ARB","uri":"http://www.wikidata.org/entity/Q7924"},
"Anhalt-Dessau":{"label":"AND","uri":"http://www.wikidata.org/entity/Q278874"},
"Anhalt":{"label":"ANH","uri":"https://www.wikidata.org/wiki/Q155578"},
"Aurich":{"label":"AUR","uri":"http://www.wikidata.org/entity/Q1801981"},
"Baden":{"label":"BAD","uri":"http://www.wikidata.org/entity/Q186320"},
"Bautzen":{"label":"BAU","uri":"http://www.wikidata.org/entity/Q1787682"},
"Bayern":{"label":"BAY","uri":"http://www.wikidata.org/entity/Q154195"},
"Bentheim":{"label":"BEN","uri":"http://www.wikidata.org/entity/Q5939"},
"Berlin":{"label":"BER","uri":"http://www.wikidata.org/entity/Q64"},
"Birkenfeld":{"label":"BIF","uri":"http://www.wikidata.org/entity/Q506329"},
"Braunschweig":{"label":"BRA","uri":""},
"Brandenburg":{"label":"BRB","uri":"https://www.wikidata.org/wiki/Q700264"},
"Breslau":{"label":"BRE","uri":"http://www.wikidata.org/entity/Q1799"},
"Bromberg":{"label":"BRO","uri":"http://www.wikidata.org/entity/Q325114"},
"Chemnitz":{"label":"CHE","uri":"http://www.wikidata.org/entity/Q1407272"},
"Clausthal":{"label":"CLA","uri":"http://www.wikidata.org/entity/Q819712"},
"Deutscher Bund":{"label":"DTB","uri":"https://www.wikidata.org/wiki/Q151624"},
"Deutsches Reich":{"label":"DTR","uri":"https://www.wikidata.org/wiki/Q43287"},
"Danzig":{"label":"DAN","uri":"http://www.wikidata.org/entity/Q479800"},
"Donaukreis":{"label":"DOK","uri":"http://www.wikidata.org/entity/Q1240941"},
"Dresden":{"label":"DRE","uri":"http://www.wikidata.org/entity/Q1731"},
"Düsseldorf":{"label":"DUE","uri":"http://www.wikidata.org/entity/Q7926"},
"Erfurt":{"label":"EFU","uri":"http://www.wikidata.org/entity/Q930404"},
"Elsaß-Lothringen":{"label":"ELL","uri":"http://www.wikidata.org/entity/Q155144"},
"Erzgebirgischer Kreis":{"label":"ERZ","uri":"http://www.wikidata.org/entity/Q1366141"},
"Freie Stadt Frankfurt":{"label":"FFM","uri":"http://www.wikidata.org/entity/Q186320"},
"Frankfurt Oder":{"label":"FFO","uri":"http://www.wikidata.org/entity/Q4024"},
"Freie Hansestadt Bremen":{"label":"FHB","uri":"http://www.wikidata.org/entity/Q24879"},
"Freie Hansestadt Hamburg":{"label":"FHH","uri":"http://www.wikidata.org/entity/Q24879"},
"Freie- und Hansestadt Lübeck":{"label":"FHL","uri":"http://www.wikidata.org/entity/Q2843"},
"Freiburg":{"label":"FRI","uri":"http://www.wikidata.org/entity/Q2833"},
"Fulda":{"label":"FUL","uri":"http://www.wikidata.org/entity/Q6434"},
"Gotha":{"label":"GTH","uri":"http://www.wikidata.org/entity/Q6986"},
"Gumbinnen":{"label":"GUM","uri":"http://www.wikidata.org/entity/Q5663"},
"Krain":{"label":"KRA","uri":"https://www.wikidata.org/wiki/Q193474"},
"Steiermark":{"label":"STM","uri":"https://www.wikidata.org/wiki/Q41358"},
"Königreich Hannover":{"label":"HAN","uri":"http://www.wikidata.org/entity/Q164079"},
"Königreich Hannover":{"label":"HAL","uri":"http://www.wikidata.org/entity/Q164079"},
"Hanau":{"label":"HAU","uri":"http://www.wikidata.org/entity/Q472875"},
"Hildesheim":{"label":"HDH","uri":"http://www.wikidata.org/entity/Q1567141"},
"Hessen-Darmstadt":{"label":"HED","uri":"http://www.wikidata.org/entity/Q20135"},
"Hessen-Homburg":{"label":"HEH","uri":"http://www.wikidata.org/entity/Q694269"},
"Hessen-Kassel":{"label":"HEK","uri":"http://www.wikidata.org/entity/Q529605"},
"Hessen-Nassau":{"label":"HNA","uri":"http://www.wikidata.org/entity/Q693356"},
"Hohnstein":{"label":"HOS","uri":"http://www.wikidata.org/entity/Q16831619"},
"Holstein":{"label":"HOL","uri":"http://www.wikidata.org/entity/Q704288"},
"Hohenzollernsche Lande":{"label":"HOH","uri":"https://www.wikidata.org/wiki/Q819762"},
"Hohenzollern-Hechingen":{"label":"HZH","uri":"http://www.wikidata.org/entity/Q673865"},
"Hohenzollern-Sigmaringen":{"label":"HZS","uri":"http://www.wikidata.org/entity/Q157013"},
"Isarkreis":{"label":"ISK","uri":"http://www.wikidata.org/entity/Q1673724"},
"Jagstkreis":{"label":"JGK","uri":"http://www.wikidata.org/entity/Q1678480"},
"Karlsruhe":{"label":"KAL","uri":"http://www.wikidata.org/entity/Q114101231"},
"Kassel":{"label":"KAS","uri":"http://www.wikidata.org/entity/Q2865"},
"Kleve":{"label":"KLE","uri":"http://www.wikidata.org/entity/Q6842"},
"Köln":{"label":"KLN","uri":"http://www.wikidata.org/entity/Q7927"},
"Koblenz":{"label":"KLZ","uri":"http://www.wikidata.org/entity/Q3104"},
"Konstanz":{"label":"KON","uri":"http://www.wikidata.org/entity/Q1355328"},
"Köslin":{"label":"KOS","uri":"https://www.wikidata.org/wiki/Q62868"},
"Königsberg":{"label":"Königsberg","uri":"http://www.wikidata.org/entity/Q531205"},
"Küstenland":{"label":"KUS","uri":"https://www.wikidata.org/wiki/Q306696"},
"Lauenburg":{"label":"LAU","uri":"http://www.wikidata.org/entity/Q313175"},
"Lübeck":{"label":"LBE","uri":"http://www.wikidata.org/entity/Q1311767"},
"Liegnitz":{"label":"LEG","uri":"http://www.wikidata.org/entity/Q205816"},
"Leipziger Kreis":{"label":"LEI","uri":"http://www.wikidata.org/entity/Q1450281"},
"Liechtenstein":{"label":"LIE","uri":"http://www.wikidata.org/entity/Q347"},
"Lippe-Detmold":{"label":"LIP","uri":"http://www.wikidata.org/entity/Q107380"},
"Lothringen":{"label":"LOT","uri":"http://www.wikidata.org/entity/Q1137"},
"Lüneburg":{"label":"LUB","uri":"http://www.wikidata.org/entity/Q1801982"},
"Luxemburg":{"label":"LUX","uri":"http://www.wikidata.org/entity/Q32"},
"Mähren":{"label":"MAE","uri":"https://www.wikidata.org/wiki/Q43266"},
"Böhmen":{"label":"BOE","uri":"https://www.wikidata.org/wiki/Q39193"},
"Kärnten":{"label":"KAE","uri":"https://www.wikidata.org/wiki/Q37985"},
"Magdeburg":{"label":"MAG","uri":"http://www.wikidata.org/entity/Q1733"},
"Mannheim":{"label":"MAN","uri":"http://www.wikidata.org/entity/Q1802313"},
"Marienwerder":{"label":"MAW","uri":"http://www.wikidata.org/entity/Q479818"},
"Main- und Tauberkreis":{"label":"MAI","uri":"http://www.wikidata.org/entity/Q106370205"},
"Mecklenburg-Schwerin":{"label":"MES","uri":"http://www.wikidata.org/entity/Q158445"},
"Mecklenburg-Strelitz":{"label":"MET","uri":"http://www.wikidata.org/entity/Q161215"},
"Mittelfranken":{"label":"MFR","uri":"http://www.wikidata.org/entity/Q10551"},
"Minden":{"label":"MIN","uri":"http://www.wikidata.org/entity/Q313969"},
"Merseburg":{"label":"MRB","uri":"http://www.wikidata.org/entity/Q896664"},
"Mittelrheinkreis":{"label":"MRK","uri":"http://www.wikidata.org/entity/Q113557270"},
"Murg- und Pfinzkreis":{"label":"MUR","uri":"http://www.wikidata.org/entity/Q114615010"},
"Münster":{"label":"MUE","uri":"http://www.wikidata.org/entity/Q7920"},
"Nassau":{"label":"NAS","uri":"http://www.wikidata.org/entity/Q449097"},
"Niederbayern":{"label":"NBA","uri":"http://www.wikidata.org/entity/Q10559"},
"Niederhessen":{"label":"NHE","uri":"http://www.wikidata.org/entity/Q882777"},
"Oberbayern":{"label":"OBA","uri":"http://www.wikidata.org/entity/Q10562"},
"Oberlausitz":{"label":"OBE","uri":"http://www.wikidata.org/entity/Q7943"},
"Oberhessen":{"label":"OBH","uri":"http://www.wikidata.org/entity/Q896499"},
"Oberösterreich":{"label":"OOE","uri":"https://www.wikidata.org/wiki/Q41967"},
"Niederösterreich":{"label":"NOE","uri":"https://www.wikidata.org/wiki/Q42497"},
"Osnabrück":{"label":"OBK","uri":"http://www.wikidata.org/entity/Q1422612"},
"Oberhessen":{"label":"OHK","uri":"https://www.wikidata.org/wiki/Q896499"},
"Oberdonaukreis":{"label":"ODK","uri":"http://www.wikidata.org/entity/Q760200"},
"Österreich":{"label":"OES","uri":"http://www.wikidata.org/entity/Q40"},
"Oberfranken":{"label":"OFR","uri":"http://www.wikidata.org/entity/Q10554"},
"Oldenburg":{"label":"OLD","uri":"http://www.wikidata.org/entity/Q693669"},
"Oberhessen":{"label":"OLH","uri":"http://www.wikidata.org/entity/Q896499"},
"Obermainkreis":{"label":"OMK","uri":"http://www.wikidata.org/entity/Q1885638"},
"Oberpfalz":{"label":"OPF","uri":"http://www.wikidata.org/entity/Q10555"},
"Oppeln":{"label":"OPP","uri":"http://www.wikidata.org/entity/Q827092"},
"Oberrheinkreis":{"label":"ORK","uri":"http://www.wikidata.org/entity/Q50407967"},
"Ostpreußen":{"label":"OSP","uri":"http://www.wikidata.org/entity/Q103801"},
"Neckarkreis":{"label":"NCK","uri":"http://www.wikidata.org/entity/Q1122124"},
"Rheinkreis":{"label":"PFL","uri":"http://www.wikidata.org/entity/Q2147860"},
"Pommern":{"label":"POM","uri":"http://www.wikidata.org/entity/Q104520"},
"Posen":{"label":"POS","uri":"http://www.wikidata.org/entity/Q635253"},
"Potsdam":{"label":"POT","uri":"http://www.wikidata.org/entity/Q827186"},
"Preußen":{"label":"PRE","uri":"http://www.wikidata.org/entity/Q27306"},
"Regenkreis":{"label":"RGK","uri":"http://www.wikidata.org/entity/Q2137422"},
"Reuß ältere Linie":{"label":"RAL","uri":""},
"Reuß-Ebersdorf":{"label":"REB","uri":"http://www.wikidata.org/entity/Q543090"},
"Rheinhessen":{"label":"RHH","uri":"http://www.wikidata.org/entity/Q17353989"},
"Rheinprovinz":{"label":"RHP","uri":"http://www.wikidata.org/entity/Q698162"},
"Reuß jüngere Linie":{"label":"RJL","uri":""},
"Reuß-Lobenstein und Ebersdorf":{"label":"RLE","uri":""},
"Reuß-Lobenstein":{"label":"RLO","uri":"http://www.wikidata.org/entity/Q509478"},
"Reuß-Schleiz":{"label":"RSC","uri":""},
"Sachsen-Altenburg":{"label":"SAB","uri":"http://www.wikidata.org/entity/Q158151"},
"Sachsen":{"label":"SAC","uri":"http://www.wikidata.org/entity/Q153015"},
"Sachsen-Hildburghausen":{"label":"SAH","uri":"http://www.wikidata.org/entity/Q281005"},
"Sachsen-Meiningen":{"label":"SAM","uri":"http://www.wikidata.org/entity/Q157710"},
"Sachsen-Coburg und Gotha":{"label":"SCG","uri":"http://www.wikidata.org/entity/Q3462133"},
"Salzburg":{"label":"SAL","uri":"https://www.wikidata.org/wiki/Q43325"},
"Schwaben":{"label":"SCH","uri":"http://www.wikidata.org/entity/Q11812551"},
"Sachsen-Coburg Saalfeld":{"label":"SCS","uri":"http://www.wikidata.org/entity/Q700663"},
"Seekreis":{"label":"SEK","uri":"http://www.wikidata.org/entity/Q106595708"},
"Sachsen-Gotha-Altenburg":{"label":"SGA","uri":"http://www.wikidata.org/entity/Q675085"},
"Schleswig-Holstein":{"label":"SHS","uri":"http://www.wikidata.org/entity/Q286977"},
"Schlesien":{"label":"SLE","uri":"http://www.wikidata.org/entity/Q81720"},
"Schaumburg-Lippe":{"label":"SLI","uri":"http://www.wikidata.org/entity/Q310650"},
"Schleswig":{"label":"SLW","uri":"http://www.wikidata.org/entity/Q501661"},
"Schwarzburg-Rudolstadt":{"label":"SRU","uri":"http://www.wikidata.org/entity/Q695316"},
"Schwarzburg-Sondershausen":{"label":"SSO","uri":"http://www.wikidata.org/entity/Q630163"},
"Starkenburg":{"label":"STB","uri":"http://www.wikidata.org/entity/Q2138196"},
"Stade":{"label":"STD","uri":"http://www.wikidata.org/entity/Q11722882"},
"Stettin":{"label":"STE","uri":"http://www.wikidata.org/entity/Q870107"},
"Stralsund":{"label":"STR","uri":"http://www.wikidata.org/entity/Q321542"},
"Stuttgart":{"label":"STU","uri":"http://www.wikidata.org/entity/Q1022"},
"Sachsen-Weimar-Eisenach":{"label":"SWE","uri":"http://www.wikidata.org/entity/Q155570"},
"Schwarzwaldkreis":{"label":"SWK","uri":"http://www.wikidata.org/entity/Q1748758"},
"Vorarlberg":{"label":"VOR","uri":"https://www.wikidata.org/wiki/Q38981"},
"Trier":{"label":"TRI","uri":"http://www.wikidata.org/entity/Q573203"},
"Tirol":{"label":"TIR","uri":"https://www.wikidata.org/wiki/Q42880"},
"Unterelsaß":{"label":"UEL","uri":"http://www.wikidata.org/entity/Q2150573"},
"Unterfranken":{"label":"UFR","uri":"http://www.wikidata.org/entity/Q10547"},
"Unterrheinkreis":{"label":"URK","uri":"http://www.wikidata.org/entity/Q105451793"},
"Untermainkreis":{"label":"UMK","uri":"http://www.wikidata.org/entity/Q2498042"},
"Vogtländischer Kreis":{"label":"VOG","uri":"http://www.wikidata.org/entity/Q2236340"},
"Waldeck":{"label":"WAL","uri":"http://www.wikidata.org/entity/Q165763"},
"Westfalen":{"label":"WFA","uri":"http://www.wikidata.org/entity/Q8614"},
"Westpreußen":{"label":"WPE","uri":"http://www.wikidata.org/entity/Q161947"},
"Württemberg":{"label":"WUE","uri":"http://www.wikidata.org/entity/Q159631"},
"Wiesbaden":{"label":"WIS","uri":"http://www.wikidata.org/entity/Q1721"},
"Zwickau":{"label":"ZWI","uri":"http://www.wikidata.org/entity/Q3778"}

}

shorthandToString={
"ACH":{"label":"Aachen","uri":"http://www.wikidata.org/entity/Q896929"},
"ADK":{"label":"Anhalt-Dessau-Köthen","uri":"http://www.wikidata.org/entity/Q2944524"},
"ALL":{"label":"Allenstein","uri":"http://www.wikidata.org/entity/Q82765"},
"ANB":{"label":"Anhalt-Bernburg","uri":"http://www.wikidata.org/entity/Q686965"},
"ANK":{"label":"Anhalt-Köthen","uri":"http://www.wikidata.org/entity/Q264970"},
"ARB":{"label":"Arnsberg","uri":"http://www.wikidata.org/entity/Q7924"},
"AND":{"label":"Anhalt-Dessau","uri":"http://www.wikidata.org/entity/Q278874"},
"ANH":{"label":"Anhalt","uri":"https://www.wikidata.org/wiki/Q155578"},
"AUP":{"label":"Aurich","uri":"http://www.wikidata.org/entity/Q1801981"},
"AUR":{"label":"Aurich","uri":"http://www.wikidata.org/entity/Q1801981"},
"BAD":{"label":"Baden","uri":"http://www.wikidata.org/entity/Q186320"},
"BAU":{"label":"Bautzen","uri":"http://www.wikidata.org/entity/Q1787682"},
"BAY":{"label":"Bayern","uri":"http://www.wikidata.org/entity/Q154195"},
"BEN":{"label":"Bentheim","uri":"http://www.wikidata.org/entity/Q5939"},
"BER":{"label":"Berlin","uri":"http://www.wikidata.org/entity/Q64"},
"BIF":{"label":"Birkenfeld","uri":"http://www.wikidata.org/entity/Q506329"},
"BOE":{"label":"Böhmen","uri":"https://www.wikidata.org/wiki/Q39193"},
"BRA":{"label":"Braunschweig","uri":""},
"BRB":{"label":"Brandenburg","uri":"https://www.wikidata.org/wiki/Q700264"},
"BRE":{"label":"Breslau","uri":"http://www.wikidata.org/entity/Q1799"},
"BRO":{"label":"Bromberg","uri":"http://www.wikidata.org/entity/Q325114"},
"CLA":{"label":"Clausthal","uri":"http://www.wikidata.org/entity/Q819712"},
"CHE":{"label":"Chemnitz","uri":"http://www.wikidata.org/entity/Q1407272"},
"DAN":{"label":"Danzig","uri":"http://www.wikidata.org/entity/Q479800"},
"DOK":{"label":"Donaukreis","uri":"http://www.wikidata.org/entity/Q1240941"},
"DRE":{"label":"Dresden","uri":"http://www.wikidata.org/entity/Q1731"},
"DUE":{"label":"Düsseldorf","uri":"http://www.wikidata.org/entity/Q7926"},
"DTB":{"label":"Deutscher Bund","uri":"https://www.wikidata.org/wiki/Q151624"},
"DTR":{"label":"Deutsches Reich","uri":"https://www.wikidata.org/wiki/Q43287"},
"EFU":{"label":"Erfurt","uri":"http://www.wikidata.org/entity/Q930404"},
"ELL":{"label":"Elsaß-Lothringen","uri":"http://www.wikidata.org/entity/Q155144"},
"ERZ":{"label":"Erzgebirgischer Kreis","uri":"http://www.wikidata.org/entity/Q1366141"},
"FFM":{"label":"Freie Stadt Frankfurt","uri":"http://www.wikidata.org/entity/Q186320"},
"FFO":{"label":"Frankfurt Oder","uri":"http://www.wikidata.org/entity/Q4024"},
"FHB":{"label":"Freie Hansestadt Bremen","uri":"http://www.wikidata.org/entity/Q24879"},
"FHH":{"label":"Freie Hansestadt Hamburg","uri":"http://www.wikidata.org/entity/Q24879"},
"FHL":{"label":"Freie- und Hansestadt Lübeck","uri":"http://www.wikidata.org/entity/Q2843"},
"FRI":{"label":"Freiburg","uri":"http://www.wikidata.org/entity/Q2833"},
"FUL":{"label":"Fulda","uri":"http://www.wikidata.org/entity/Q6434"},
"GTH":{"label":"Gotha","uri":"http://www.wikidata.org/entity/Q6986"},
"GUM":{"label":"Gumbinnen","uri":"http://www.wikidata.org/entity/Q5663"},
"HAN":{"label":"Königreich Hannover","uri":"http://www.wikidata.org/entity/Q164079"},
"HAL":{"label":"Königreich Hannover","uri":"http://www.wikidata.org/entity/Q164079"},
"HAU":{"label":"Hanau","uri":"http://www.wikidata.org/entity/Q472875"},
"HDH":{"label":"Hildesheim","uri":"http://www.wikidata.org/entity/Q1567141"},
"HED":{"label":"Hessen-Darmstadt","uri":"http://www.wikidata.org/entity/Q20135"},
"HEH":{"label":"Hessen-Homburg","uri":"http://www.wikidata.org/entity/Q694269"},
"HEK":{"label":"Hessen-Kassel","uri":"http://www.wikidata.org/entity/Q529605"},
"HNA":{"label":"Hessen-Nassau","uri":"http://www.wikidata.org/entity/Q693356"},
"HOL":{"label":"Holstein","uri":"http://www.wikidata.org/entity/Q704288"},
"HOH":{"label":"Hohenzollernsche Lande","uri":"https://www.wikidata.org/wiki/Q819762"},
"HOS":{"label":"Hohnstein","uri":"http://www.wikidata.org/entity/Q16831619"},
"HZH":{"label":"Hohenzollern-Hechingen","uri":"http://www.wikidata.org/entity/Q673865"},
"HZS":{"label":"Hohenzollern-Sigmaringen","uri":"http://www.wikidata.org/entity/Q157013"},
"ISK":{"label":"Isarkreis","uri":"http://www.wikidata.org/entity/Q1673724"},
"JGK":{"label":"Jagstkreis","uri":"http://www.wikidata.org/entity/Q1678480"},
"KAL":{"label":"Karlsruhe","uri":"http://www.wikidata.org/entity/Q114101231"},
"KAS":{"label":"Kassel","uri":"http://www.wikidata.org/entity/Q2865"},
"KAE":{"label":"Kärnten","uri":"https://www.wikidata.org/wiki/Q37985"},
"KLE":{"label":"Kleve","uri":"http://www.wikidata.org/entity/Q6842"},
"KLN":{"label":"Köln","uri":"http://www.wikidata.org/entity/Q7927"},
"KLZ":{"label":"Koblenz","uri":"http://www.wikidata.org/entity/Q3104"},
"KON":{"label":"Konstanz","uri":"http://www.wikidata.org/entity/Q1355328"},
"KOS":{"label":"Köslin","uri":"https://www.wikidata.org/wiki/Q62868"},
"KUS":{"label":"Küstenland","uri":"https://www.wikidata.org/wiki/Q306696"},
"KNB":{"label":"Königsberg","uri":"http://www.wikidata.org/entity/Q531205"},
"KRA":{"label":"Krain","uri":"https://www.wikidata.org/wiki/Q193474"},
"LAU":{"label":"Lauenburg","uri":"http://www.wikidata.org/entity/Q313175"},
"LBE":{"label":"Lübeck","uri":"http://www.wikidata.org/entity/Q1311767"},
"LEG":{"label":"Liegnitz","uri":"http://www.wikidata.org/entity/Q205816"},
"LEI":{"label":"Leipziger Kreis","uri":"http://www.wikidata.org/entity/Q1450281"},
"LIE":{"label":"Liechtenstein","uri":"http://www.wikidata.org/entity/Q347"},
"LIP":{"label":"Lippe-Detmold","uri":"http://www.wikidata.org/entity/Q107380"},
"LOT":{"label":"Lothringen","uri":"http://www.wikidata.org/entity/Q1137"},
"LUB":{"label":"Lüneburg","uri":"http://www.wikidata.org/entity/Q1801982"},
"LUX":{"label":"Luxemburg","uri":"http://www.wikidata.org/entity/Q32"},
"MAG":{"label":"Magdeburg","uri":"http://www.wikidata.org/entity/Q1733"},
"MAE":{"label":"Mähren","uri":"https://www.wikidata.org/wiki/Q43266"},
"MAI":{"label":"Main- und Tauberkreis","uri":"http://www.wikidata.org/entity/Q106370205"},
"MAN":{"label":"Mannheim","uri":"http://www.wikidata.org/entity/Q1802313"},
"MAW":{"label":"Marienwerder","uri":"http://www.wikidata.org/entity/Q479818"},
"MES":{"label":"Mecklenburg-Schwerin","uri":"http://www.wikidata.org/entity/Q158445"},
"MET":{"label":"Mecklenburg-Strelitz","uri":"http://www.wikidata.org/entity/Q161215"},
"MFR":{"label":"Mittelfranken","uri":"http://www.wikidata.org/entity/Q10551"},
"MIN":{"label":"Minden","uri":"http://www.wikidata.org/entity/Q313969"},
"MRB":{"label":"Merseburg","uri":"http://www.wikidata.org/entity/Q896664"},
"MRK":{"label":"Mittelrheinkreis","uri":"http://www.wikidata.org/entity/Q113557270"},
"MUE":{"label":"Münster","uri":"http://www.wikidata.org/entity/Q7920"},
"MUR":{"label":"Murg- und Pfinzkreis","uri":"http://www.wikidata.org/entity/Q114615010"},
"NAS":{"label":"Nassau","uri":"http://www.wikidata.org/entity/Q449097"},
"NBA":{"label":"Niederbayern","uri":"http://www.wikidata.org/entity/Q10559"},
"NHE":{"label":"Niederhessen","uri":"http://www.wikidata.org/entity/Q882777"},
"NOE":{"label":"Niederösterreich","uri":"https://www.wikidata.org/wiki/Q42497"},
"OBA":{"label":"Oberbayern","uri":"http://www.wikidata.org/entity/Q10562"},
"OBE":{"label":"Oberlausitz","uri":"http://www.wikidata.org/entity/Q7943"},
"OBH":{"label":"Oberhessen","uri":"http://www.wikidata.org/entity/Q896499"},
"OBK":{"label":"Osnabrück","uri":"http://www.wikidata.org/entity/Q1422612"},
"OBP":{"label":"Osnabrück","uri":"http://www.wikidata.org/entity/Q1422612"},
"OHK":{"label":"Oberhessen","uri":"https://www.wikidata.org/wiki/Q896499"},
"ODK":{"label":"Oberdonaukreis","uri":"http://www.wikidata.org/entity/Q760200"},
"OES":{"label":"Österreich","uri":"http://www.wikidata.org/entity/Q40"},
"OFR":{"label":"Oberfranken","uri":"http://www.wikidata.org/entity/Q10554"},
"OLD":{"label":"Oldenburg","uri":"http://www.wikidata.org/entity/Q693669"},
"OLH":{"label":"Oberhessen","uri":"http://www.wikidata.org/entity/Q896499"},
"OMK":{"label":"Obermainkreis","uri":"http://www.wikidata.org/entity/Q1885638"},
"OOE":{"label":"Oberösterreich","uri":"https://www.wikidata.org/wiki/Q41967"},
"OPF":{"label":"Oberpfalz","uri":"http://www.wikidata.org/entity/Q10555"},
"OPP":{"label":"Oppeln","uri":"http://www.wikidata.org/entity/Q827092"},
"ORK":{"label":"Oberrheinkreis","uri":"http://www.wikidata.org/entity/Q50407967"},
"OSP":{"label":"Ostpreußen","uri":"http://www.wikidata.org/entity/Q103801"},
"NCK":{"label":"Neckarkreis","uri":"http://www.wikidata.org/entity/Q1122124"},
"NEK":{"label":"Neckarkreis","uri":"http://www.wikidata.org/entity/Q1122124"},
"PFL":{"label":"Rheinkreis","uri":"http://www.wikidata.org/entity/Q2147860"},
"POM":{"label":"Pommern","uri":"http://www.wikidata.org/entity/Q104520"},
"POR":{"label":"Posen","uri":"http://www.wikidata.org/entity/Q635253"},
"POS":{"label":"Posen","uri":"http://www.wikidata.org/entity/Q635253"},
"POT":{"label":"Potsdam","uri":"http://www.wikidata.org/entity/Q827186"},
"PRE":{"label":"Preußen","uri":"http://www.wikidata.org/entity/Q27306"},
"PRU":{"label":"Preußen","uri":"http://www.wikidata.org/entity/Q27306"},
"RAL":{"label":"Reuß ältere Linie","uri":""},
"REB":{"label":"Reuß-Ebersdorf","uri":"http://www.wikidata.org/entity/Q543090"},
"RGK":{"label":"Regenkreis","uri":"http://www.wikidata.org/entity/Q2137422"},
"RHH":{"label":"Rheinhessen","uri":"http://www.wikidata.org/entity/Q17353989"},
"RHP":{"label":"Rheinprovinz","uri":"http://www.wikidata.org/entity/Q698162"},
"RJL":{"label":"Reuß jüngere Linie","uri":""},
"RLE":{"label":"Reuß-Lobenstein und Ebersdorf","uri":""},
"RLO":{"label":"Reuß-Lobenstein","uri":"http://www.wikidata.org/entity/Q509478"},
"RTK":{"label":"Rezatkreis","uri":"http://www.wikidata.org/entity/Q1709460"},
"RSC":{"label":"Reuß-Schleiz","uri":""},
"SAB":{"label":"Sachsen-Altenburg","uri":"http://www.wikidata.org/entity/Q158151"},
"SAC":{"label":"Sachsen","uri":"http://www.wikidata.org/entity/Q153015"},
"SAP":{"label":"Sachsen","uri":"http://www.wikidata.org/entity/Q153015"},
"SAL":{"label":"Salzburg","uri":"https://www.wikidata.org/wiki/Q43325"},
"SAH":{"label":"Sachsen-Hildburghausen","uri":"http://www.wikidata.org/entity/Q281005"},
"SAM":{"label":"Sachsen-Meiningen","uri":"http://www.wikidata.org/entity/Q157710"},
"SCG":{"label":"Sachsen-Coburg und Gotha","uri":"http://www.wikidata.org/entity/Q3462133"},
"SCH":{"label":"Schwaben","uri":"http://www.wikidata.org/entity/Q11812551"},
"SCS":{"label":"Sachsen-Coburg Saalfeld","uri":"http://www.wikidata.org/entity/Q700663"},
"SEK":{"label":"Seekreis","uri":"http://www.wikidata.org/entity/Q106595708"},
"SGA":{"label":"Sachsen-Gotha-Altenburg","uri":"http://www.wikidata.org/entity/Q675085"},
"SHS":{"label":"Schleswig-Holstein","uri":"http://www.wikidata.org/entity/Q286977"},
"SLE":{"label":"Schlesien","uri":"http://www.wikidata.org/entity/Q81720"},
"SLO":{"label":"Schlesien","uri":"https://www.wikidata.org/wiki/Q298874"},
"SLI":{"label":"Schaumburg-Lippe","uri":"http://www.wikidata.org/entity/Q310650"},
"SLW":{"label":"Schleswig","uri":"http://www.wikidata.org/entity/Q501661"},
"SCL":{"label":"Schleswig","uri":"http://www.wikidata.org/entity/Q501661"},
"SRU":{"label":"Schwarzburg-Rudolstadt","uri":"http://www.wikidata.org/entity/Q695316"},
"SSO":{"label":"Schwarzburg-Sondershausen","uri":"http://www.wikidata.org/entity/Q630163"},
"STB":{"label":"Starkenburg","uri":"http://www.wikidata.org/entity/Q2138196"},
"STM":{"label":"Steiermark","uri":"https://www.wikidata.org/wiki/Q41358"},
"STD":{"label":"Stade","uri":"http://www.wikidata.org/entity/Q11722882"},
"STP":{"label":"Stade","uri":"http://www.wikidata.org/entity/Q11722882"},
"STE":{"label":"Stettin","uri":"http://www.wikidata.org/entity/Q870107"},
"STR":{"label":"Stralsund","uri":"http://www.wikidata.org/entity/Q321542"},
"STU":{"label":"Stuttgart","uri":"http://www.wikidata.org/entity/Q1022"},
"SWE":{"label":"Sachsen-Weimar-Eisenach","uri":"http://www.wikidata.org/entity/Q155570"},
"SWK":{"label":"Schwarzwaldkreis","uri":"http://www.wikidata.org/entity/Q1748758"},
"TRI":{"label":"Trier","uri":"http://www.wikidata.org/entity/Q573203"},
"TIR":{"label":"Tirol","uri":"https://www.wikidata.org/wiki/Q42880"},
"UEL":{"label":"Unterelsaß","uri":"http://www.wikidata.org/entity/Q2150573"},
"UFR":{"label":"Unterfranken","uri":"http://www.wikidata.org/entity/Q10547"},
"UMK":{"label":"Untermainkreis","uri":"http://www.wikidata.org/entity/Q2498042"},
"URK":{"label":"Unterrheinkreis","uri":"http://www.wikidata.org/entity/Q105451793"},
"VOR":{"label":"Vorarlberg","uri":"https://www.wikidata.org/wiki/Q38981"},
"VOG":{"label":"Vogtländischer Kreis","uri":"http://www.wikidata.org/entity/Q2236340"},
"WAL":{"label":"Waldeck","uri":"http://www.wikidata.org/entity/Q165763"},
"WFA":{"label":"Westfalen","uri":"http://www.wikidata.org/entity/Q8614"},
"WPE":{"label":"Westpreußen","uri":"http://www.wikidata.org/entity/Q161947"},
"WEP":{"label":"Westpreußen","uri":"http://www.wikidata.org/entity/Q161947"},
"WUE":{"label":"Württemberg","uri":"http://www.wikidata.org/entity/Q159631"},
"WIS":{"label":"Wiesbaden","uri":"http://www.wikidata.org/entity/Q1721"},
"ZWI":{"label":"Zwickau","uri":"http://www.wikidata.org/entity/Q3778"}
}

statsprefixes={
"Bev":{"label":"population","uri":"http://www.wikidata.org/entity/Q33829","unit":""},
"Eis":{"label":"pig iron production","uri":"http://www.wikidata.org/entity/Q901785","unit":"http://www.ontology-of-units-of-measure.org/resource/om-2/tonne"},
"Erz":{"label":"ore production","uri":"http://www.wikidata.org/entity/Q102798","unit":"http://www.ontology-of-units-of-measure.org/resource/om-2/tonne"},
"BrKoh":{"label":"brown coal production","uri":"http://www.wikidata.org/entity/Q156267","unit":"http://www.ontology-of-units-of-measure.org/resource/om-2/tonne"},
"StKoh":{"label":"bituminous coal production","uri":"http://www.wikidata.org/entity/Q732607","unit":"http://www.ontology-of-units-of-measure.org/resource/om-2/tonne"},
"Sta":{"label":"steel production","uri":"http://www.wikidata.org/entity/Q11427","unit":"http://www.ontology-of-units-of-measure.org/resource/om-2/tonne"}
}

def createSOSAPopulationHistory(featureuri,featlabel,resgraph,csvfile):
    feature="http://www.wikidata.org/entity/Q33829"
    featurelabel="population"
    csvred=""
    unit=""
    #print("CSVFILE: "+str(csvfile))
    if "Bev" in csvfile:
        feature=statsprefixes["Bev"]["uri"]
        featurelabel=statsprefixes["Bev"]["label"]
        if "gesamt" in csvfile:
            csvred=csvfile.replace("Bev","").replace("-gesamt.csv","").replace("Prov","").replace("csv/","")
        else:
            csvred=csvfile[csvfile.find("-")+1:].replace("Bev","").replace(".csv","").replace("Prov","").replace("csv/","")
        unit=statsprefixes["Bev"]["unit"]
    elif "Eis" in csvfile:
        feature=statsprefixes["Eis"]["uri"]
        featurelabel=statsprefixes["Eis"]["label"] 
        if "gesamt" in csvfile:
            csvred=csvfile.replace("Eis","").replace("-gesamt.csv","").replace("Prov","").replace("csv/","")
        else:
            csvred=csvfile[csvfile.find("-")+1:].replace("Eis","").replace(".csv","").replace("Prov","").replace("csv/","")
        unit=statsprefixes["Eis"]["unit"]
    elif "Erz" in csvfile:
        feature=statsprefixes["Erz"]["uri"]
        featurelabel=statsprefixes["Erz"]["label"]        
        if "gesamt" in csvfile:
            csvred=csvfile.replace("Erz","").replace("-gesamt.csv","").replace("Prov","").replace("csv/","")
        else:
            csvred=csvfile[csvfile.find("-")+1:].replace("Erz","").replace(".csv","").replace("Prov","").replace("csv/","")
        unit=statsprefixes["Erz"]["unit"]
    elif "BrKoh" in csvfile:
        feature=statsprefixes["BrKoh"]["uri"]
        featurelabel=statsprefixes["BrKoh"]["label"]   
        if "gesamt" in csvfile:
            csvred=csvfile.replace("BrKoh","").replace("-gesamt.csv","").replace("Prov","").replace("csv/","")
        else:
            csvred=csvfile[csvfile.find("-")+1:].replace("BrKoh","").replace(".csv","").replace("Prov","").replace("csv/","")
        unit=statsprefixes["BrKoh"]["unit"]
    elif "StKoh" in csvfile:
        feature=statsprefixes["StKoh"]["uri"]
        featurelabel=statsprefixes["StKoh"]["label"] 
        if "gesamt" in csvfile:
            csvred=csvfile.replace("StKoh","").replace("-gesamt.csv","").replace("Prov","").replace("csv/","")
        else:
            csvred=csvfile[csvfile.find("-")+1:].replace("StKoh","").replace(".csv","").replace("Prov","").replace("csv/","")
        unit=statsprefixes["StKoh"]["unit"]
    elif "Sta" in csvfile:
        feature=statsprefixes["Sta"]["uri"]
        featurelabel=statsprefixes["Sta"]["label"] 
        if "gesamt" in csvfile:
            csvred=csvfile.replace("Sta","").replace("-gesamt.csv","").replace("Prov","").replace("csv/","")
        else:
            csvred=csvfile[csvfile.find("-")+1:].replace("Sta","").replace(".csv","").replace("Prov","").replace("csv/","")
        unit=statsprefixes["Sta"]["unit"]
    #print("CSVRED: "+csvred)
    featurelabel2=featurelabel.replace(" ","_")
    if csvred.startswith("OES") and len(csvred)>3:
        csvred=csvred.replace("OES","")
    if csvred in shorthandToString:
        featlabel=shorthandToString[csvred]["label"]
        featureuri=datanamespace+csvred
    else:
        print("MISSINGSHORTHAND: "+str(csvred))
        print("FROM FILE: "+str(csvfile))
    with open(csvfile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        lastyear=-1
        resgraph=createMetadataForInstance(featureuri,resgraph)
        resgraph.add((URIRef(featureuri),URIRef("http://www.w3.org/ns/sosa/hasObservation"),URIRef(featureuri+"_"+str(featurelabel2))))
        resgraph.add((URIRef("http://www.w3.org/ns/sosa/hasObservation"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/sosa/ObservationCollection")))
        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(str(featurelabel)+" of "+str(featlabel),lang="en")))
        resgraph.add((URIRef(featureuri),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(str(featlabel),lang="en")))
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {"; ".join(row)}')
                line_count += 1
            else:
                if row[0]!="" and row[0].isnumeric() and row[1]!="":
                    try:
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)),URIRef("http://www.w3.org/2000/01/rdf-schema#member"),URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0])))
                        resgraph=createMetadataForInstance(featureuri+"_"+str(featurelabel2),resgraph)
                        if len(row)>2 and row[3]!="":
                            resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0]),URIRef("http://www.wikidata.org/prop/direct/P1480"),URIRef(sources[str(row[3])]["uri"]))) 
                            resgraph.add((URIRef(sources[str(row[3])]["uri"]),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(sources[str(row[3])]["label"],lang="en"))) 
                            resgraph.add((URIRef("http://www.wikidata.org/prop/direct/P1480"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                            resgraph.add((URIRef("http://www.wikidata.org/prop/direct/P1480"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("sourcing circumstances",lang="en")))                            
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0]),URIRef("http://www.w3.org/ns/sosa/hasFeatureOfInterest"),URIRef(featureuri)))
                        resgraph.add((URIRef(featureuri),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/sosa/Platform")))
                        #resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0]+"_acquisition"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/sosa/Sampling")))
                        #resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0]+"_acquisition"),URIRef("http://www.w3.org/ns/sosa/implements"),URIRef("population_acquisition")))
                        #resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0]+"_acquisition"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("Population Acquisition of "+str(featureuri)+" in year "+str(row[0]),lang="en")))
                        #resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+row[0]+"_acquisition"),URIRef("http://www.w3.org/ns/sosa/observes"),URIRef("http://www.wikidata.org/entity/Q33829")))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/sosa/Observation")))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(featlabel+" "+str(featurelabel)+" observation for year "+str(row[0]).replace(" ","_"),lang="en")))
                        if unit=="":
                            resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")),URIRef("http://www.w3.org/ns/sosa/hasSimpleResult"),Literal(str(row[1]),datatype="http://www.w3.org/2001/XMLSchema#integer")))        
                        else:
                            resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")),URIRef("http://www.w3.org/ns/sosa/hasResult"),URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_result")))
                            resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_result"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasUnit"),URIRef(unit)))
                            resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_result"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(featlabel+" "+str(featurelabel)+" observation result for year "+str(row[0]).replace(" ","_"),lang="en")))
                            resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_result"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasNumericalValue"),Literal(str(row[1]),datatype="http://www.w3.org/2001/XMLSchema#integer")))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")),URIRef("http://www.w3.org/ns/sosa/observedProperty"),URIRef(feature)))
                        resgraph.add((URIRef("http://www.wikidata.org/entity/Q33829"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/sosa/ObservableProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/phenomenonTime"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/2000/01/rdf-schema#member"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasUnit"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/observedProperty"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/observes"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/implements"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/hasFeatureOfInterest"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/hasSimpleResult"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")))
                        resgraph.add((URIRef("http://www.w3.org/ns/sosa/hasResult"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
                        resgraph.add((URIRef("http://www.w3.org/2006/time#inXSDgYear"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")))
                        resgraph.add((URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasNumericalValue"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")))
                        resgraph.add((URIRef(feature),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#NamedIndividual"))) 
                        resgraph.add((URIRef(feature),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(featurelabel)))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")),URIRef("http://www.w3.org/ns/sosa/phenomenonTime"),URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_te")))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_te"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2006/time#Instant")))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_te"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(featlabel+" "+str(featurelabel)+" observation time instant for year "+str(row[0]),lang="en")))
                        resgraph.add((URIRef(featureuri+"_"+str(featurelabel2)+"_"+str(row[0]).replace(" ","_")+"_te"),URIRef("http://www.w3.org/2006/time#inXSDgYear"),Literal(str(row[0]),datatype="http://www.w3.org/2001/XMLSchema#gYear")))
                    except Exception as e:
                        print(e)
                    lastyear=row[0]
                line_count += 1
        #print(f'Processed {line_count} lines.')
    return resgraph

def createPopulationDensity(featuri,resgraph,label,value):
    resgraph.add((URIRef(featuri),URIRef("http://dbpedia.org/ontology/populationDensity"),URIRef(featuri+"_popden")))
    resgraph.add((URIRef("http://dbpedia.org/ontology/populationDensity"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
    resgraph.add((URIRef(featuri+"_popden"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("Population Density of "+str(label))))
    resgraph.add((URIRef(featuri+"_popden"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.wikidata.org/entity/Q22856")))
    resgraph.add((URIRef("http://www.wikidata.org/entity/Q22856"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("Population Density",lang="en")))
    resgraph.add((URIRef(featuri+"_popden"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasValue"),URIRef(featuri+"_popden_value")))
    resgraph.add((URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasValue"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("has value",lang="en")))
    resgraph.add((URIRef(featuri+"_popden_value"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("Population Density Value of "+str(label))))
    resgraph.add((URIRef(featuri+"_popden_value"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/Measure")))
    resgraph.add((URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasNumericalValue"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("has numerical value",lang="en")))
    resgraph.add((URIRef(featuri+"_popden_value"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasNumericalValue"),Literal(value,datatype="http://www.w3.org/2001/XMLSchema#double")))
    resgraph.add((URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasUnit"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("has unit",lang="en")))
    resgraph.add((URIRef(featuri+"_popden_value"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/hasUnit"),URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/peoplePerSquareKilometre")))
    resgraph.add((URIRef("http://www.ontology-of-units-of-measure.org/resource/om-2/peoplePerSquareKilometre"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("people per square kilometre",lang="en")))
    return resgraph

def createMetadataForInstance(instance,resgraph):
    resgraph.add((URIRef(instance),URIRef("http://purl.org/dc/terms/creator"),URIRef(datanamespace+"Andreas_Kunz")))
    resgraph.add((URIRef("http://purl.org/dc/terms/creator"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#ObjectProperty")))
    resgraph.add((URIRef(datanamespace+"Andreas_Kunz"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://xmlns.com/foaf/0.1/Person")))
    resgraph.add((URIRef(datanamespace+"Andreas_Kunz"),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("Andreas Kunz")))
    resgraph.add((URIRef(datanamespace+"Andreas_Kunz"),URIRef("http://xmlns.com/foaf/0.1/firstName"),Literal("Andreas")))
    resgraph.add((URIRef(datanamespace+"Andreas_Kunz"),URIRef("http://xmlns.com/foaf/0.1/familyName"),Literal("Kunz")))
    resgraph.add((URIRef(instance),URIRef("http://purl.org/dc/terms/created"),Literal("2008",datatype="http://www.w3.org/2001/XMLSchema#gYear")))
    resgraph.add((URIRef("http://purl.org/dc/terms/created"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")))
    resgraph.add((URIRef("http://purl.org/dc/terms/publisher"),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/2002/07/owl#DatatypeProperty")))
    resgraph.add((URIRef(instance),URIRef("http://purl.org/dc/terms/publisher"),Literal("IEG")))
    return resgraph

statg=Graph()
g=Graph()
for dir_, _, files in os.walk("csv"):
    for filename in files:
        f = filename
        # checking if it is a file
        if str(f).endswith(".csv"):
            createSOSAPopulationHistory("","",statg,"csv/"+f) 
statg.serialize("hgis_stats.ttl")        