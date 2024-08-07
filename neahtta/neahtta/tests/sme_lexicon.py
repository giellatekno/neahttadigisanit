# -*- encoding: utf-8 -*-

import os
import tempfile
import unittest

import neahtta

from .lexicon import (
    BasicTests,
    ParadigmGenerationTests,
    WordLookupAPITests,
    WordLookupDetailTests,
    WordLookupTests,
    form_contains,
    form_doesnt_contain,
)

wordforms_that_shouldnt_fail = [
    (("sme", "nob"), "sihke"),
    (("sme", "nob"), "mannat"),
    (("sme", "nob"), "manai"),
    (("sme", "nob"), "Gállábártnit"),
    (("nob", "sme"), "drikke"),
    (("nob", "sme"), "forbi"),
    (("nob", "sme"), "stige"),
    # This one contains a blank definition node, but translations.
    (("nob", "sme"), "sette"),
    # Copied some words from a previous test log. May need to go through
    # these and do things about results instead of just testing that
    # 404s and 500s aren't returned
    # Test that SoMe paths work
    (("SoMe", "nob"), "geahcci"),
    (("SoMe", "nob"), "leazzaba"),
    (("SoMe", "nob"), "leažžaba"),
    (("SoMe", "nob"), "munnuide"),
    # Test that finn paths work: TODO: -- ensure analysis returned?
    (("fin", "sme"), "menijä"),
    (("fin", "sme"), "menijää"),
    (("fin", "sme"), "menisi"),
    (("fin", "sme"), "mennä"),
    # test that nob->sme placenames work
    (("nob", "sme"), "Austerrike"),
    (("nob", "sme"), "Noreg"),
    (("nob", "sme"), "austerrikisk"),
    (("nob", "sme"), "skilnad"),
    (("nob", "sme"), "Østerrike"),
    (("nob", "sme"), "Aust-Noreg"),
    # sme->fin
    (("sme", "fin"), "leažžaba"),
    # placenames returned
    (("sme", "nob"), "Gálbbejávrrit"),
    (("sme", "nob"), "Gállábártnit"),
    # misc inflections
    (("sme", "nob"), "diehtit"),
    (("sme", "nob"), "girjaide"),
    (("sme", "nob"), "girji"),
    (("sme", "nob"), "girjiide"),
    (("sme", "nob"), "girjjaid"),
    (("sme", "nob"), "girjjaide"),
    (("sme", "nob"), "girjjiide"),
    (("sme", "nob"), "guovdageaidnulaš"),
    (("sme", "nob"), "leaččan"),
    (("sme", "nob"), "leažžaba"),
    (("sme", "nob"), "manai"),
    (("sme", "nob"), "manan"),
    (("sme", "nob"), "mannat"),
    (("sme", "nob"), "moai"),
    (("sme", "nob"), "muinna"),
    (("sme", "nob"), "mun"),
    (("sme", "nob"), "munnje"),
    (("sme", "nob"), "munnos"),
    (("sme", "nob"), "munnuide"),
    (("sme", "nob"), "mánnageahčči"),
    (("sme", "nob"), "mánná"),
    (("sme", "nob"), "neahkameahttun"),
    (("sme", "nob"), "sihke"),
    (("sme", "nob"), "sihkestan"),
    (("sme", "nob"), "sihkestit"),
    # random sampling from user activity log
    (("SoMe", "nob"), "duddet"),
    (("SoMe", "nob"), "etter"),
    (("SoMe", "nob"), "jeg"),
    (("fin", "sme"), "aika"),
    (("fin", "sme"), "asia"),
    (("fin", "sme"), "etsiä"),
    (("fin", "sme"), "hakea"),
    (("fin", "sme"), "huitaista"),
    (("fin", "sme"), "hänen kanssa"),
    (("fin", "sme"), "hänen kanssaan"),
    (("fin", "sme"), "johonkin"),
    (("fin", "sme"), "johtaja"),
    (("fin", "sme"), "joulu"),
    (("fin", "sme"), "järjestys"),
    (("fin", "sme"), "kanssa"),
    (("fin", "sme"), "kirjoittaa"),
    (("fin", "sme"), "laktása"),
    (("fin", "sme"), "laktásit"),
    (("fin", "sme"), "loma"),
    (("fin", "sme"), "lomalla"),
    (("fin", "sme"), "missä"),
    (("fin", "sme"), "ohjaaja"),
    (("fin", "sme"), "opetella"),
    (("fin", "sme"), "opiskella"),
    (("fin", "sme"), "oppia"),
    (("fin", "sme"), "pitäjä"),
    (("fin", "sme"), "poika"),
    (("fin", "sme"), "selvä (asiasta)"),
    (("fin", "sme"), "selvä"),
    (("fin", "sme"), "sitä"),
    (("fin", "sme"), "talo"),
    (("fin", "sme"), "varata"),
    (("fin", "sme"), "vetäjä"),
    (("fin", "sme"), "vetää"),
    (("fin", "sme"), "vetæjæ"),
    (("fin", "sme"), "yhdessä"),
    (("fin", "sme"), "ášši"),
    (("fin", "sme"), "ääni"),
    (("nob", "sme"), "Ferdig"),
    (("nob", "sme"), "Vil du spise"),
    (("nob", "sme"), "aktiviteter"),
    (("nob", "sme"), "amanu"),
    (("nob", "sme"), "andre"),
    (("nob", "sme"), "bare"),
    (("nob", "sme"), "barnehage"),
    (("nob", "sme"), "begynner"),
    (("nob", "sme"), "begynte"),
    (("nob", "sme"), "begŧnte"),
    (("nob", "sme"), "best"),
    (("nob", "sme"), "beste"),
    (("nob", "sme"), "bestemor"),
    (("nob", "sme"), "bestevenn"),
    (("nob", "sme"), "betydning"),
    (("nob", "sme"), "bibliotek"),
    (("nob", "sme"), "bok"),
    (("nob", "sme"), "bred"),
    (("nob", "sme"), "bruke tid"),
    (("nob", "sme"), "brus"),
    (("nob", "sme"), "buss"),
    (("nob", "sme"), "butikk"),
    (("nob", "sme"), "både"),
    (("nob", "sme"), "bøker"),
    (("nob", "sme"), "børste"),
    (("nob", "sme"), "car port"),
    (("nob", "sme"), "cirka"),
    (("nob", "sme"), "dag"),
    (("nob", "sme"), "danse"),
    (("nob", "sme"), "deksel"),
    (("nob", "sme"), "deltaker"),
    (("nob", "sme"), "der"),
    (("nob", "sme"), "dessert"),
    (("nob", "sme"), "dette"),
    (("nob", "sme"), "dette er"),
    (("nob", "sme"), "dette"),
    (("nob", "sme"), "dra"),
    (("nob", "sme"), "dra på tur"),
    (("nob", "sme"), "dåp"),
    (("nob", "sme"), "eller"),
    (("nob", "sme"), "elv"),
    (("nob", "sme"), "ennå"),
    (("nob", "sme"), "eple"),
    (("nob", "sme"), "erfaren"),
    (("nob", "sme"), "etter"),
    (("nob", "sme"), "fakta"),
    (("nob", "sme"), "far"),
    (("nob", "sme"), "favoritt"),
    (("nob", "sme"), "favorittmat"),
    (("nob", "sme"), "ferdig"),
    (("nob", "sme"), "ferdigđ"),
    (("nob", "sme"), "fin"),
    (("nob", "sme"), "finne"),
    (("nob", "sme"), "fint"),
    (("nob", "sme"), "fiske"),
    (("nob", "sme"), "fjortende"),
    (("nob", "sme"), "fjæra"),
    (("nob", "sme"), "fjæreområde"),
    (("nob", "sme"), "flokken"),
    (("nob", "sme"), "flytter"),
    (("nob", "sme"), "folk"),
    (("nob", "sme"), "forberede"),
    (("nob", "sme"), "forskaling"),
    (("nob", "sme"), "fotball"),
    (("nob", "sme"), "fysioterapeut"),
    (("nob", "sme"), "først"),
    (("nob", "sme"), "gang"),
    (("nob", "sme"), "garasje"),
    (("nob", "sme"), "grunn"),
    (("nob", "sme"), "grunnmur"),
    (("nob", "sme"), "grøt"),
    (("nob", "sme"), "gå"),
    (("nob", "sme"), "gård"),
    (("nob", "sme"), "ha"),
    (("nob", "sme"), "hakket"),
    (("nob", "sme"), "har"),
    (("nob", "sme"), "helligdag"),
    (("nob", "sme"), "hjelp"),
    (("nob", "sme"), "hobby"),
    (("nob", "sme"), "hobbyer"),
    (("nob", "sme"), "hun (har)"),
    (("nob", "sme"), "hun"),
    (("nob", "sme"), "hus"),
    (("nob", "sme"), "hvor"),
    (("nob", "sme"), "hytte"),
    (("nob", "sme"), "høne unge"),
    (("nob", "sme"), "høne"),
    (("nob", "sme"), "høneunge"),
    (("nob", "sme"), "i dag"),
    (("nob", "sme"), "ikke"),
    (("nob", "sme"), "informasjon om"),
    (("nob", "sme"), "informasjon"),
    (("nob", "sme"), "ingredienser"),
    (("nob", "sme"), "inngredienser"),
    (("nob", "sme"), "interesse"),
    (("nob", "sme"), "interesser"),
    (("nob", "sme"), "iskrem"),
    (("nob", "sme"), "jeg"),
    (("nob", "sme"), "jente"),
    (("nob", "sme"), "jobb"),
    (("nob", "sme"), "jobber"),
    (("nob", "sme"), "k"),
    (("nob", "sme"), "kake"),
    (("nob", "sme"), "kald vestavind"),
    (("nob", "sme"), "kald østavind"),
    (("nob", "sme"), "kald"),
    (("nob", "sme"), "kirke"),
    (("nob", "sme"), "kjæreste"),
    (("nob", "sme"), "kjøttdeig"),
    (("nob", "sme"), "klokken"),
    (("nob", "sme"), "kommende"),
    (("nob", "sme"), "kvittering"),
    (("nob", "sme"), "kylling salat"),
    (("nob", "sme"), "kylling"),
    (("nob", "sme"), "kyllingklubb"),
    (("nob", "sme"), "kyllingklubbe"),
    (("nob", "sme"), "kyllingsalat"),
    (("nob", "sme"), "kyllinh"),
    (("nob", "sme"), "lage"),
    (("nob", "sme"), "land"),
    (("nob", "sme"), "lasagne"),
    (("nob", "sme"), "le"),
    (("nob", "sme"), "leamaw"),
    (("nob", "sme"), "lege"),
    (("nob", "sme"), "leke"),
    (("nob", "sme"), "lese"),
    (("nob", "sme"), "ligge"),
    (("nob", "sme"), "ligger ved"),
    (("nob", "sme"), "liker ikke"),
    (("nob", "sme"), "liker"),
    (("nob", "sme"), "liten"),
    (("nob", "sme"), "liturgi"),
    (("nob", "sme"), "mandager"),
    (("nob", "sme"), "mat"),
    (("nob", "sme"), "men"),
    (("nob", "sme"), "menneske"),
    (("nob", "sme"), "mennesket"),
    (("nob", "sme"), "middag"),
    (("nob", "sme"), "mihkal sin mor heter"),
    (("nob", "sme"), "mis lea"),
    (("nob", "sme"), "multebær"),
    (("nob", "sme"), "multer"),
    (("nob", "sme"), "mye"),
    (("nob", "sme"), "måle"),
    (("nob", "sme"), "måned"),
    (("nob", "sme"), "måneder"),
    (("nob", "sme"), "møte verb"),
    (("nob", "sme"), "møte"),
    (("nob", "sme"), "natur"),
    (("nob", "sme"), "naturbruk"),
    (("nob", "sme"), "naturen"),
    (("nob", "sme"), "neste"),
    (("nob", "sme"), "nisse"),
    (("nob", "sme"), "noe"),
    (("nob", "sme"), "oeft"),
    (("nob", "sme"), "ofte"),
    (("nob", "sme"), "også"),
    (("nob", "sme"), "olje"),
    (("nob", "sme"), "om høsten"),
    (("nob", "sme"), "om sommeren"),
    (("nob", "sme"), "om vinteren"),
    (("nob", "sme"), "om"),
    (("nob", "sme"), "omsorgssenter"),
    (("nob", "sme"), "omtrent"),
    (("nob", "sme"), "onsdag"),
    (("nob", "sme"), "opp"),
    (("nob", "sme"), "opplegg"),
    (("nob", "sme"), "oppskrift"),
    (("nob", "sme"), "ost"),
    (("nob", "sme"), "ovdal"),
    (("nob", "sme"), "pappa"),
    (("nob", "sme"), "patent"),
    (("nob", "sme"), "pent"),
    (("nob", "sme"), "pepper"),
    (("nob", "sme"), "plass"),
    (("nob", "sme"), "plukke bær"),
    (("nob", "sme"), "postkontor"),
    (("nob", "sme"), "potte"),
    (("nob", "sme"), "purre"),
    (("nob", "sme"), "purreløk"),
    (("nob", "sme"), "på ordentlig"),
    (("nob", "sme"), "raring"),
    (("nob", "sme"), "regning"),
    (("nob", "sme"), "reise"),
    (("nob", "sme"), "renne"),
    (("nob", "sme"), "ri"),
    (("nob", "sme"), "riktig"),
    (("nob", "sme"), "rydde"),
    (("nob", "sme"), "sage"),
    (("nob", "sme"), "salat"),
    (("nob", "sme"), "salt"),
    (("nob", "sme"), "samboer"),
    (("nob", "sme"), "samisk"),
    (("nob", "sme"), "samtale"),
    (("nob", "sme"), "saus"),
    (("nob", "sme"), "sin"),
    (("nob", "sme"), "skatt"),
    (("nob", "sme"), "skatter"),
    (("nob", "sme"), "slutter"),
    (("nob", "sme"), "slå"),
    (("nob", "sme"), "som"),
    (("nob", "sme"), "sommer"),
    (("nob", "sme"), "spille"),
    (("nob", "sme"), "spilt"),
    (("nob", "sme"), "spise"),
    (("nob", "sme"), "stabble"),
    (("nob", "sme"), "stable"),
    (("nob", "sme"), "sted"),
    (("nob", "sme"), "sterk vind"),
    (("nob", "sme"), "stjele"),
    (("nob", "sme"), "stolt"),
    (("nob", "sme"), "stryk"),
    (("nob", "sme"), "sy"),
    (("nob", "sme"), "sytten"),
    (("nob", "sme"), "så"),
    (("nob", "sme"), "søster"),
    (("nob", "sme"), "ta"),
    (("nob", "sme"), "takstol"),
    (("nob", "sme"), "tar"),
    (("nob", "sme"), "tekst"),
    (("nob", "sme"), "telefonnummer"),
    (("nob", "sme"), "tidligere"),
    (("nob", "sme"), "tie"),
    (("nob", "sme"), "tilbe"),
    (("nob", "sme"), "tjuefjerde"),
    (("nob", "sme"), "tomat"),
    (("nob", "sme"), "tomatpure"),
    (("nob", "sme"), "trenge"),
    (("nob", "sme"), "trening"),
    (("nob", "sme"), "trivelig"),
    (("nob", "sme"), "tvinge"),
    (("nob", "sme"), "tysk"),
    (("nob", "sme"), "underholde"),
    (("nob", "sme"), "unge"),
    (("nob", "sme"), "vakker"),
    (("nob", "sme"), "vann"),
    (("nob", "sme"), "vant"),
    (("nob", "sme"), "vaske opp"),
    (("nob", "sme"), "vaske"),
    (("nob", "sme"), "ved siden av"),
    (("nob", "sme"), "vegg"),
    (("nob", "sme"), "veggeme"),
    (("nob", "sme"), "veggene"),
    (("nob", "sme"), "vegger"),
    (("nob", "sme"), "veidnes"),
    (("nob", "sme"), "veidnesklubben"),
    (("nob", "sme"), "veldig"),
    (("nob", "sme"), "venn"),
    (("nob", "sme"), "verden"),
    (("nob", "sme"), "vestavind"),
    (("nob", "sme"), "videregående skole"),
    (("nob", "sme"), "videregående"),
    (("nob", "sme"), "viessu"),
    (("nob", "sme"), "vind"),
    (("nob", "sme"), "vurdere"),
    (("nob", "sme"), "våkne"),
    (("nob", "sme"), "vår"),
    (("nob", "sme"), "å ha"),
    (("nob", "sme"), "å møte"),
    (("nob", "sme"), "økonomi"),
    (("sme", "fin"), "ahte"),
    (("sme", "fin"), "almmiguovlu"),
    (("sme", "fin"), "asia"),
    (("sme", "fin"), "bagadalli"),
    (("sme", "fin"), "bealljái"),
    (("sme", "fin"), "beasat"),
    (("sme", "fin"), "beassat"),
    (("sme", "fin"), "biegga"),
    (("sme", "fin"), "boagusta"),
    (("sme", "fin"), "boagustit"),
    (("sme", "fin"), "boahtin"),
    (("sme", "fin"), "botnje"),
    (("sme", "fin"), "buddáduvvat"),
    (("sme", "fin"), "buot"),
    (("sme", "fin"), "báhcit"),
    (("sme", "fin"), "coggat"),
    (("sme", "fin"), "dadjá"),
    (("sme", "fin"), "dalle"),
    (("sme", "fin"), "de"),
    (("sme", "fin"), "diibmu"),
    (("sme", "fin"), "doalli"),
    (("sme", "fin"), "dohpo"),
    (("sme", "fin"), "doppe"),
    (("sme", "fin"), "dovdat"),
    (("sme", "fin"), "dušše"),
    (("sme", "fin"), "dállu"),
    (("sme", "fin"), "dáppehan"),
    (("sme", "fin"), "ealli"),
    (("sme", "fin"), "eamidin"),
    (("sme", "fin"), "fadda"),
    (("sme", "fin"), "fas"),
    (("sme", "fin"), "fáippastit"),
    (("sme", "fin"), "gal"),
    (("sme", "fin"), "garra"),
    (("sme", "fin"), "geahčadit"),
    (("sme", "fin"), "giige"),
    (("sme", "fin"), "gitta"),
    (("sme", "fin"), "guovttos"),
    (("sme", "fin"), "gutna"),
    (("sme", "fin"), "gávdno"),
    (("sme", "fin"), "hutka"),
    (("sme", "fin"), "hutkat"),
    (("sme", "fin"), "hutkkálaš"),
    (("sme", "fin"), "háv"),
    (("sme", "fin"), "hávdádit"),
    (("sme", "fin"), "jienas"),
    (("sme", "fin"), "jietnadan"),
    (("sme", "fin"), "jođiheaddji"),
    (("sme", "fin"), "juo"),
    (("sme", "fin"), "juohke"),
    (("sme", "fin"), "juoidá"),
    (("sme", "fin"), "juos"),
    (("sme", "fin"), "juosat"),
    (("sme", "fin"), "kanssa"),
    (("sme", "fin"), "kirjoittaa"),
    (("sme", "fin"), "kirjottaa"),
    (("sme", "fin"), "lahkonit"),
    (("sme", "fin"), "leamaš"),
    (("sme", "fin"), "liegga"),
    (("sme", "fin"), "liikká"),
    (("sme", "fin"), "lomalla"),
    (("sme", "fin"), "mearkugohte"),
    (("sme", "fin"), "miessi"),
    (("sme", "fin"), "misiin"),
    (("sme", "fin"), "missä"),
    (("sme", "fin"), "mohkki"),
    (("sme", "fin"), "mojohallat"),
    (("sme", "fin"), "mot"),
    (("sme", "fin"), "muhto"),
    (("sme", "fin"), "muhtumis"),
    (("sme", "fin"), "máhta"),
    (("sme", "fin"), "máhttit"),
    (("sme", "fin"), "naba"),
    (("sme", "fin"), "nebe"),
    (("sme", "fin"), "njammat"),
    (("sme", "fin"), "nu"),
    (("sme", "fin"), "nuppis"),
    (("sme", "fin"), "oaidná"),
    (("sme", "fin"), "olbmot"),
    (("sme", "fin"), "olgeš"),
    (("sme", "fin"), "olu"),
    (("sme", "fin"), "orui"),
    (("sme", "fin"), "ovddabealde"),
    (("sme", "fin"), "ovddal"),
    (("sme", "fin"), "roava"),
    (("sme", "fin"), "ruovgat"),
    (("sme", "fin"), "ráfálaš"),
    (("sme", "fin"), "ráigánit"),
    (("sme", "fin"), "sevii"),
    (("sme", "fin"), "stivrejeaddji"),
    (("sme", "fin"), "suohkan"),
    (("sme", "fin"), "teapmi"),
    (("sme", "fin"), "vadjat"),
    (("sme", "fin"), "veahás"),
    (("sme", "fin"), "veaháš"),
    (("sme", "fin"), "viegahallat"),
    (("sme", "fin"), "vuollegis"),
    (("sme", "fin"), "vuollái"),
    (("sme", "fin"), "vuot"),
    (("sme", "fin"), "váldi"),
    (("sme", "fin"), "váldobargu"),
    (("sme", "fin"), "álddagas"),
    (("sme", "fin"), "álddu"),
    (("sme", "fin"), "áldu"),
    (("sme", "fin"), "čohka"),
    (("sme", "fin"), "čuhppe"),
    (("sme", "fin"), "čuččodit"),
    (("sme", "fin"), "čábbát"),
    (("sme", "nob"), "Eanet"),
    (("sme", "nob"), "algan"),
    (("sme", "nob"), "alggan"),
    (("sme", "nob"), "alggos"),
    (("sme", "nob"), "algit"),
    (("sme", "nob"), "almmuhangeasku"),
    (("sme", "nob"), "almmuhit"),
    (("sme", "nob"), "astat"),
    (("sme", "nob"), "astta"),
    (("sme", "nob"), "asttá"),
    (("sme", "nob"), "astá"),
    (("sme", "nob"), "beaivi"),
    (("sme", "nob"), "bearal"),
    (("sme", "nob"), "bearralat"),
    (("sme", "nob"), "bidjat"),
    (("sme", "nob"), "bihca"),
    (("sme", "nob"), "bihcabáhcahasaid"),
    (("sme", "nob"), "bija"),
    (("sme", "nob"), "boastakantuvra"),
    (("sme", "nob"), "bohccebiddji"),
    (("sme", "nob"), "bohttu"),
    (("sme", "nob"), "buozas"),
    (("sme", "nob"), "bágget"),
    (("sme", "nob"), "báhcahasaid"),
    (("sme", "nob"), "coggat"),
    (("sme", "nob"), "da lea"),
    (("sme", "nob"), "dat lea"),
    (("sme", "nob"), "deltaker"),
    (("sme", "nob"), "dette er"),
    (("sme", "nob"), "dette"),
    (("sme", "nob"), "diehttelas"),
    (("sme", "nob"), "dieva"),
    (("sme", "nob"), "diibmui"),
    (("sme", "nob"), "diibmuii"),
    (("sme", "nob"), "dine"),
    (("sme", "nob"), "dinet"),
    (("sme", "nob"), "dohkalaš"),
    (("sme", "nob"), "dohkkalaš"),
    (("sme", "nob"), "dohkket"),
    (("sme", "nob"), "dohkkálaš"),
    (("sme", "nob"), "dohkálaš"),
    (("sme", "nob"), "dolvo"),
    (("sme", "nob"), "duddjot"),
    (("sme", "nob"), "duhkoraddat"),
    (("sme", "nob"), "duhkordallat"),
    (("sme", "nob"), "dulka"),
    (("sme", "nob"), "duogábealde"),
    (("sme", "nob"), "duogáš"),
    (("sme", "nob"), "dáhpáhuvvat"),
    (("sme", "nob"), "dállu"),
    (("sme", "nob"), "eaibmi"),
    (("sme", "nob"), "favoriht"),
    (("sme", "nob"), "favorihtt"),
    (("sme", "nob"), "favorihtta"),
    (("sme", "nob"), "favorihttamusihkka"),
    (("sme", "nob"), "favoritt"),
    (("sme", "nob"), "feaskkir"),
    (("sme", "nob"), "ferdig"),
    (("sme", "nob"), "firon"),
    (("sme", "nob"), "fiskegrateng"),
    (("sme", "nob"), "fysioterapevta"),
    (("sme", "nob"), "garvodan"),
    (("sme", "nob"), "gaskabiebmu"),
    (("sme", "nob"), "gaskavahkku"),
    (("sme", "nob"), "gassada"),
    (("sme", "nob"), "geahpas"),
    (("sme", "nob"), "geahppa"),
    (("sme", "nob"), "geardi"),
    (("sme", "nob"), "girjerájus"),
    (("sme", "nob"), "goarrrut"),
    (("sme", "nob"), "goarrut"),
    (("sme", "nob"), "guite"),
    (("sme", "nob"), "gulaskuddan"),
    (("sme", "nob"), "gulaskuddat"),
    (("sme", "nob"), "guoibmi"),
    (("sme", "nob"), "guoika"),
    (("sme", "nob"), "gusta"),
    (("sme", "nob"), "guštá"),
    (("sme", "nob"), "gárggiideapmi"),
    (("sme", "nob"), "gárvodan"),
    (("sme", "nob"), "gárvodit"),
    (("sme", "nob"), "gávpi"),
    (("sme", "nob"), "heivemin"),
    (("sme", "nob"), "heivvemin"),
    (("sme", "nob"), "helmmot"),
    (("sme", "nob"), "hupmat"),
    (("sme", "nob"), "hálla"),
    (("sme", "nob"), "hállat"),
    (("sme", "nob"), "hápmá"),
    (("sme", "nob"), "hápmása"),
    (("sme", "nob"), "hápmásažžan"),
    (("sme", "nob"), "hárjánan"),
    (("sme", "nob"), "hárvenaš"),
    (("sme", "nob"), "i"),
    (("sme", "nob"), "idja"),
    (("sme", "nob"), "issorasat"),
    (("sme", "nob"), "iđitbiebmu"),
    (("sme", "nob"), "jaskkodit"),
    (("sme", "nob"), "jed"),
    (("sme", "nob"), "jeg"),
    (("sme", "nob"), "jente"),
    (("sme", "nob"), "juoga"),
    (("sme", "nob"), "juoidá"),
    (("sme", "nob"), "kirku"),
    (("sme", "nob"), "kylling"),
    (("sme", "nob"), "lahka"),
    (("sme", "nob"), "lahkai"),
    (("sme", "nob"), "laktása"),
    (("sme", "nob"), "laktásit"),
    (("sme", "nob"), "leamaš"),
    (("sme", "nob"), "leaš"),
    (("sme", "nob"), "lihkan"),
    (("sme", "nob"), "liibmet"),
    (("sme", "nob"), "lisster"),
    (("sme", "nob"), "logaldalli"),
    (("sme", "nob"), "luđiide"),
    (("sme", "nob"), "lágan"),
    (("sme", "nob"), "láhka"),
    (("sme", "nob"), "láhkai"),
    (("sme", "nob"), "mandager"),
    (("sme", "nob"), "maŋŋel"),
    (("sme", "nob"), "mohkki"),
    (("sme", "nob"), "mun"),
    (("sme", "nob"), "mánnodat"),
    (("sme", "nob"), "mánnu"),
    (("sme", "nob"), "mánáidgárdi"),
    (("sme", "nob"), "måle"),
    (("sme", "nob"), "målte"),
    (("sme", "nob"), "neaktit"),
    (("sme", "nob"), "nieida"),
    (("sme", "nob"), "nigát"),
    (("sme", "nob"), "niidii"),
    (("sme", "nob"), "nuollat"),
    (("sme", "nob"), "oadju"),
    (("sme", "nob"), "ohccis"),
    (("sme", "nob"), "ohcis"),
    (("sme", "nob"), "olggoš"),
    (("sme", "nob"), "olla"),
    (("sme", "nob"), "ollašuhttit"),
    (("sme", "nob"), "ollu"),
    (("sme", "nob"), "olmmoš"),
    (("sme", "nob"), "orbbeš"),
    (("sme", "nob"), "orda"),
    (("sme", "nob"), "ore"),
    (("sme", "nob"), "ovdal"),
    (("sme", "nob"), "ovdamus"),
    (("sme", "nob"), "rissegierragat"),
    (("sme", "nob"), "rivttes"),
    (("sme", "nob"), "ruhtaheađis"),
    (("sme", "nob"), "ruhtahoidu"),
    (("sme", "nob"), "ruhtahođis"),
    (("sme", "nob"), "sadji"),
    (("sme", "nob"), "sahet"),
    (("sme", "nob"), "salat"),
    (("sme", "nob"), "seaidni"),
    (("sme", "nob"), "seakka"),
    (("sme", "nob"), "skuohppu"),
    (("sme", "nob"), "smávis"),
    (("sme", "nob"), "spillet"),
    (("sme", "nob"), "spábbačiekčan"),
    (("sme", "nob"), "stoahkat"),
    (("sme", "nob"), "stresset"),
    (("sme", "nob"), "suoládit"),
    (("sme", "nob"), "sádjá"),
    (("sme", "nob"), "sádjái"),
    (("sme", "nob"), "sámegielgalba"),
    (("sme", "nob"), "sárgá"),
    (("sme", "nob"), "tienas"),
    (("sme", "nob"), "uhcci"),
    (("sme", "nob"), "ullu"),
    (("sme", "nob"), "unni"),
    (("sme", "nob"), "vahku"),
    (("sme", "nob"), "vai"),
    (("sme", "nob"), "valdit"),
    (("sme", "nob"), "vullojuvvon"),
    (("sme", "nob"), "vuortnuhit"),
    (("sme", "nob"), "vuovdnái"),
    (("sme", "nob"), "váibbas"),
    (("sme", "nob"), "válddahagas"),
    (("sme", "nob"), "váldit"),
    (("sme", "nob"), "Ávdnasat"),
    (("sme", "nob"), "Áđđestaddi"),
    (("sme", "nob"), "álgit"),
    (("sme", "nob"), "čeabetbáddi"),
    (("sme", "nob"), "čivga"),
    (("sme", "nob"), "čohkohallat"),
    (("sme", "nob"), "čohkun"),
    (("sme", "nob"), "čuohppat"),
    (("sme", "nob"), "čuojaha"),
    (("sme", "nob"), "čáppat"),
]

# TODO: testcase for null lookup-- is returning 500 but should not be,
# but also need to make sure this fix sticks around.

#   /lookup/sme/nob/?callback=jQuery3094203984029384&lookup=&lemmatize=true

# TODO: use api lookups to determine that rule overrides are formatting
# things correctly

# TODO:  tunealla+v1: tunealla vs. tunealla+v2: tunnealla

# TODO: vmax ruovttueana

# TODO: testcase for miniparadigms, both pregenerated:

paradigm_generation_tests = [
    # source, target, lemma, error_msg, paradigm_test
    ###  - http://localhost:5000/detail/sme/nob/iige.json
    ###  - localhost:5000/detail/sme/nob/manne.json
    # ... and automatically generated
    ###  - Pregenerated forms from mini_paradigm
    (
        "sme",
        "nob",
        "mun",
        "Not generating from mini_paradigm",
        form_contains(set(["munnje", "mus", "munin"])),
    ),
    ###  - A:
    ###     - http://localhost:5000/detail/sme/nob/ruoksat.json
    ###     - test that context is found as well as paradigm
    ###     - test that +Use/NGminip forms are not generated
    (
        "sme",
        "nob",
        "heittot",
        "Dialectical forms present",
        form_doesnt_contain(set(["heittohat", "heittohut", "heittohit"])),
    ),
    ###  - A + context="bivttas":  heittot
    ###     - http://localhost:5000/detail/sme/nob/heittot.html
    ("sme", "nob", "heittot", "Context missing", form_contains(set(["heittogis"]))),
    ###  - A + context="báddi":  guhkki
    ###     - http://localhost:5000/detail/sme/nob/guhkki.html
    ("sme", "nob", "guhkki", "Context missing", form_contains(set(["guhkes"]))),
    ###  - Num + context="gápmagat":  guokte
    ###     - http://localhost:5000/detail/sme/nob/guokte.html
    ("sme", "nob", "guokte", "Context missing", form_contains(set(["guovttit"]))),
    ###  - N + illpl="no": eahketroađđi, sihkarvuohta, skuvlaáigi
    (
        "sme",
        "nob",
        "eahketroađđi",
        "Illative plural present",
        form_doesnt_contain(set(["eahketrođiide"])),
    ),
    ###  - N Prop Sg: Norga, Ruoŧŧa
    ###     - http://localhost:5000/detail/sme/nob/Ruoŧŧa.html
    (
        "sme",
        "nob",
        "Ruoŧŧa",
        "Forms not generated",
        form_contains(set(["Ruoŧa bokte", "Ruŧŧii", "Ruoŧas"])),
    ),
    ###  - N Prop Pl: Iččát
    ###     - <l pos="N" type="Prop" nr="Pl">Iččát</l>
    (
        "sme",
        "nob",
        "Iččát",
        "Forms not generated",
        form_contains(set(["Iččáid bokte", "Iččáide", "Iččáin"])),
    ),
    ("sme", "nob", "mannat", "Forms not generated", form_contains(set(["manan"]))),
    (
        "sme",
        "nob",
        "deaivvadit",
        "Overgenerating forms",
        form_doesnt_contain(set(["deaivvadan"])),
    ),
    (
        "sme",
        "nob",
        "girji",
        "Overgenerating forms. Possible tag filtration issue.",
        form_doesnt_contain(set(["girjje"])),
    ),
    ###  - N
    ###    - <l pos="N" type="G3">sámeášši</l>
    (
        "sme",
        "nob",
        "sámeášši",
        "Forms not generated",
        form_contains(set(["sámeášši", "sámeáššái", "sámeáššiiguin"])),
    ),
    #     u'Ráisa',
    #     u'dálkkádagat',
    #     u'deaivvadit' - check that Pl3 deaivvadedje and deaivvadit are
    #     generated
    ###  - V: boahtit
    ###     - check context, and paradigm:
    ###     - http://localhost:5000/detail/sme/nob/boahtit.json
    # TODO: this test
    ###  - V + context="dat", v + context="sii"
    ###     - check context, and that paradigm is not generated for 1st person
    ###     - http://localhost:5000/detail/sme/nob/ciellat.html
    ###     - http://localhost:5000/detail/sme/nob/deaivvadit.html
    # TODO: this test
    ###  - N
    # TODO: find most common kinds of nouns
]


class WordLookupTests(WordLookupTests):
    def test_single_word(self):
        """Test that the basic idea of testing will work.
        If there's a problem here, this is a problem. ;)
        """
        lang_pair, form = wordforms_that_shouldnt_fail[0]

        base = "/%s/%s/" % lang_pair
        rv = self.app.post(
            base,
            data={
                "lookup": form,
            },
        )

        assert "sihke" in rv.data
        assert "både" in rv.data.decode("utf-8")
        self.assertEqual(rv.status_code, 200)


class BasicTests(BasicTests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class WordLookupDetailTests(WordLookupDetailTests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class WordLookupAPITests(WordLookupAPITests):
    wordforms_that_shouldnt_fail = wordforms_that_shouldnt_fail


class ParadigmGenerationTests(ParadigmGenerationTests):
    paradigm_generation_tests = paradigm_generation_tests


vmax = [
    # source, target, lemma, error_msg, paradigm_test
    (
        "sme",
        "nob",
        "ruovttueana",
        "Not generating from mini_paradigm",
        form_contains(
            set(
                [
                    "ruovttueanan",
                ]
            )
        ),
    ),
]


class VMax(ParadigmGenerationTests):
    paradigm_generation_tests = vmax


class ParadigmSelectionTest(WordLookupTests):
    """These are really only for testing specifics in the paradigm
    directory structure the code, and don't need to be run as generation
    as a whole is tested above.
    """

    def test_misc_paradigms(self):
        with self.current_app.app_context():
            from paradigms import ParadigmConfig

            lookups = (
                self.current_app.morpholexicon.lookup(
                    "mannat", source_lang="sme", target_lang="nob"
                )
                + self.current_app.morpholexicon.lookup(
                    "Ráisa", source_lang="sme", target_lang="nob"
                )
                + self.current_app.morpholexicon.lookup(
                    "dálkkádagat", source_lang="sme", target_lang="nob"
                )
                + self.current_app.morpholexicon.lookup(
                    "álgoálbmotášši", source_lang="sme", target_lang="nob"
                )
                + self.current_app.morpholexicon.lookup(
                    "Dálmmát", source_lang="sme", target_lang="nob"
                )
                + self.current_app.morpholexicon.lookup(
                    "Gállábártnit", source_lang="sme", target_lang="nob"
                )
                + self.current_app.morpholexicon.lookup(
                    "Iččát", source_lang="sme", target_lang="nob"
                )
            )

            pc = self.current_app.morpholexicon.paradigms
            for node, analyses in lookups:
                print("Testing: ", node, analyses)
                print(pc.get_paradigm("sme", node, analyses, debug=True))
                print("--")
