# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import os
import tempfile
import unittest

import neahtta

from .lexicon import (BasicTests, ParadigmGenerationTests,
                      WordLookupAPITests,
                      WordLookupDetailTests, WordLookupTests, form_contains,
                      form_doesnt_contain)

wordforms_that_shouldnt_fail = [
    (('sme', 'nob'), u'sihke'),
    (('sme', 'nob'), u'mannat'),
    (('sme', 'nob'), u'manai'),
    (('sme', 'nob'), u'Gállábártnit'),
    (('nob', 'sme'), u'drikke'),
    (('nob', 'sme'), u'forbi'),
    (('nob', 'sme'), u'stige'),

    # This one contains a blank definition node, but translations.
    (('nob', 'sme'), u'sette'),

    # Copied some words from a previous test log. May need to go through
    # these and do things about results instead of just testing that
    # 404s and 500s aren't returned

    # Test that SoMe paths work
    (('SoMe', 'nob'), u'geahcci'),
    (('SoMe', 'nob'), u'leazzaba'),
    (('SoMe', 'nob'), u'leažžaba'),
    (('SoMe', 'nob'), u'munnuide'),

    # Test that finn paths work: TODO: -- ensure analysis returned?
    (('fin', 'sme'), u'menijä'),
    (('fin', 'sme'), u'menijää'),
    (('fin', 'sme'), u'menisi'),
    (('fin', 'sme'), u'mennä'),

    # test that nob->sme placenames work
    (('nob', 'sme'), u'Austerrike'),
    (('nob', 'sme'), u'Noreg'),
    (('nob', 'sme'), u'austerrikisk'),
    (('nob', 'sme'), u'skilnad'),
    (('nob', 'sme'), u'Østerrike'),
    (('nob', 'sme'), u'Aust-Noreg'),

    # sme->fin
    (('sme', 'fin'), u'leažžaba'),

    # placenames returned
    (('sme', 'nob'), u'Gálbbejávrrit'),
    (('sme', 'nob'), u'Gállábártnit'),

    # misc inflections
    (('sme', 'nob'), u'diehtit'),
    (('sme', 'nob'), u'girjaide'),
    (('sme', 'nob'), u'girji'),
    (('sme', 'nob'), u'girjiide'),
    (('sme', 'nob'), u'girjjaid'),
    (('sme', 'nob'), u'girjjaide'),
    (('sme', 'nob'), u'girjjiide'),
    (('sme', 'nob'), u'guovdageaidnulaš'),
    (('sme', 'nob'), u'leaččan'),
    (('sme', 'nob'), u'leažžaba'),
    (('sme', 'nob'), u'manai'),
    (('sme', 'nob'), u'manan'),
    (('sme', 'nob'), u'mannat'),
    (('sme', 'nob'), u'moai'),
    (('sme', 'nob'), u'muinna'),
    (('sme', 'nob'), u'mun'),
    (('sme', 'nob'), u'munnje'),
    (('sme', 'nob'), u'munnos'),
    (('sme', 'nob'), u'munnuide'),
    (('sme', 'nob'), u'mánnageahčči'),
    (('sme', 'nob'), u'mánná'),
    (('sme', 'nob'), u'neahkameahttun'),
    (('sme', 'nob'), u'sihke'),
    (('sme', 'nob'), u'sihkestan'),
    (('sme', 'nob'), u'sihkestit'),

    # random sampling from user activity log
    (('SoMe', 'nob'), u'duddet'),
    (('SoMe', 'nob'), u'etter'),
    (('SoMe', 'nob'), u'jeg'),
    (('fin', 'sme'), u'aika'),
    (('fin', 'sme'), u'asia'),
    (('fin', 'sme'), u'etsiä'),
    (('fin', 'sme'), u'hakea'),
    (('fin', 'sme'), u'huitaista'),
    (('fin', 'sme'), u'hänen kanssa'),
    (('fin', 'sme'), u'hänen kanssaan'),
    (('fin', 'sme'), u'johonkin'),
    (('fin', 'sme'), u'johtaja'),
    (('fin', 'sme'), u'joulu'),
    (('fin', 'sme'), u'järjestys'),
    (('fin', 'sme'), u'kanssa'),
    (('fin', 'sme'), u'kirjoittaa'),
    (('fin', 'sme'), u'laktása'),
    (('fin', 'sme'), u'laktásit'),
    (('fin', 'sme'), u'loma'),
    (('fin', 'sme'), u'lomalla'),
    (('fin', 'sme'), u'missä'),
    (('fin', 'sme'), u'ohjaaja'),
    (('fin', 'sme'), u'opetella'),
    (('fin', 'sme'), u'opiskella'),
    (('fin', 'sme'), u'oppia'),
    (('fin', 'sme'), u'pitäjä'),
    (('fin', 'sme'), u'poika'),
    (('fin', 'sme'), u'selvä (asiasta)'),
    (('fin', 'sme'), u'selvä'),
    (('fin', 'sme'), u'sitä'),
    (('fin', 'sme'), u'talo'),
    (('fin', 'sme'), u'varata'),
    (('fin', 'sme'), u'vetäjä'),
    (('fin', 'sme'), u'vetää'),
    (('fin', 'sme'), u'vetæjæ'),
    (('fin', 'sme'), u'yhdessä'),
    (('fin', 'sme'), u'ášši'),
    (('fin', 'sme'), u'ääni'),
    (('nob', 'sme'), u'Ferdig'),
    (('nob', 'sme'), u'Vil du spise'),
    (('nob', 'sme'), u'aktiviteter'),
    (('nob', 'sme'), u'amanu'),
    (('nob', 'sme'), u'andre'),
    (('nob', 'sme'), u'bare'),
    (('nob', 'sme'), u'barnehage'),
    (('nob', 'sme'), u'begynner'),
    (('nob', 'sme'), u'begynte'),
    (('nob', 'sme'), u'begŧnte'),
    (('nob', 'sme'), u'best'),
    (('nob', 'sme'), u'beste'),
    (('nob', 'sme'), u'bestemor'),
    (('nob', 'sme'), u'bestevenn'),
    (('nob', 'sme'), u'betydning'),
    (('nob', 'sme'), u'bibliotek'),
    (('nob', 'sme'), u'bok'),
    (('nob', 'sme'), u'bred'),
    (('nob', 'sme'), u'bruke tid'),
    (('nob', 'sme'), u'brus'),
    (('nob', 'sme'), u'buss'),
    (('nob', 'sme'), u'butikk'),
    (('nob', 'sme'), u'både'),
    (('nob', 'sme'), u'bøker'),
    (('nob', 'sme'), u'børste'),
    (('nob', 'sme'), u'car port'),
    (('nob', 'sme'), u'cirka'),
    (('nob', 'sme'), u'dag'),
    (('nob', 'sme'), u'danse'),
    (('nob', 'sme'), u'deksel'),
    (('nob', 'sme'), u'deltaker'),
    (('nob', 'sme'), u'der'),
    (('nob', 'sme'), u'dessert'),
    (('nob', 'sme'), u'dette'),
    (('nob', 'sme'), u'dette er'),
    (('nob', 'sme'), u'dette'),
    (('nob', 'sme'), u'dra'),
    (('nob', 'sme'), u'dra på tur'),
    (('nob', 'sme'), u'dåp'),
    (('nob', 'sme'), u'eller'),
    (('nob', 'sme'), u'elv'),
    (('nob', 'sme'), u'ennå'),
    (('nob', 'sme'), u'eple'),
    (('nob', 'sme'), u'erfaren'),
    (('nob', 'sme'), u'etter'),
    (('nob', 'sme'), u'fakta'),
    (('nob', 'sme'), u'far'),
    (('nob', 'sme'), u'favoritt'),
    (('nob', 'sme'), u'favorittmat'),
    (('nob', 'sme'), u'ferdig'),
    (('nob', 'sme'), u'ferdigđ'),
    (('nob', 'sme'), u'fin'),
    (('nob', 'sme'), u'finne'),
    (('nob', 'sme'), u'fint'),
    (('nob', 'sme'), u'fiske'),
    (('nob', 'sme'), u'fjortende'),
    (('nob', 'sme'), u'fjæra'),
    (('nob', 'sme'), u'fjæreområde'),
    (('nob', 'sme'), u'flokken'),
    (('nob', 'sme'), u'flytter'),
    (('nob', 'sme'), u'folk'),
    (('nob', 'sme'), u'forberede'),
    (('nob', 'sme'), u'forskaling'),
    (('nob', 'sme'), u'fotball'),
    (('nob', 'sme'), u'fysioterapeut'),
    (('nob', 'sme'), u'først'),
    (('nob', 'sme'), u'gang'),
    (('nob', 'sme'), u'garasje'),
    (('nob', 'sme'), u'grunn'),
    (('nob', 'sme'), u'grunnmur'),
    (('nob', 'sme'), u'grøt'),
    (('nob', 'sme'), u'gå'),
    (('nob', 'sme'), u'gård'),
    (('nob', 'sme'), u'ha'),
    (('nob', 'sme'), u'hakket'),
    (('nob', 'sme'), u'har'),
    (('nob', 'sme'), u'helligdag'),
    (('nob', 'sme'), u'hjelp'),
    (('nob', 'sme'), u'hobby'),
    (('nob', 'sme'), u'hobbyer'),
    (('nob', 'sme'), u'hun (har)'),
    (('nob', 'sme'), u'hun'),
    (('nob', 'sme'), u'hus'),
    (('nob', 'sme'), u'hvor'),
    (('nob', 'sme'), u'hytte'),
    (('nob', 'sme'), u'høne unge'),
    (('nob', 'sme'), u'høne'),
    (('nob', 'sme'), u'høneunge'),
    (('nob', 'sme'), u'i dag'),
    (('nob', 'sme'), u'ikke'),
    (('nob', 'sme'), u'informasjon om'),
    (('nob', 'sme'), u'informasjon'),
    (('nob', 'sme'), u'ingredienser'),
    (('nob', 'sme'), u'inngredienser'),
    (('nob', 'sme'), u'interesse'),
    (('nob', 'sme'), u'interesser'),
    (('nob', 'sme'), u'iskrem'),
    (('nob', 'sme'), u'jeg'),
    (('nob', 'sme'), u'jente'),
    (('nob', 'sme'), u'jobb'),
    (('nob', 'sme'), u'jobber'),
    (('nob', 'sme'), u'k'),
    (('nob', 'sme'), u'kake'),
    (('nob', 'sme'), u'kald vestavind'),
    (('nob', 'sme'), u'kald østavind'),
    (('nob', 'sme'), u'kald'),
    (('nob', 'sme'), u'kirke'),
    (('nob', 'sme'), u'kjæreste'),
    (('nob', 'sme'), u'kjøttdeig'),
    (('nob', 'sme'), u'klokken'),
    (('nob', 'sme'), u'kommende'),
    (('nob', 'sme'), u'kvittering'),
    (('nob', 'sme'), u'kylling salat'),
    (('nob', 'sme'), u'kylling'),
    (('nob', 'sme'), u'kyllingklubb'),
    (('nob', 'sme'), u'kyllingklubbe'),
    (('nob', 'sme'), u'kyllingsalat'),
    (('nob', 'sme'), u'kyllinh'),
    (('nob', 'sme'), u'lage'),
    (('nob', 'sme'), u'land'),
    (('nob', 'sme'), u'lasagne'),
    (('nob', 'sme'), u'le'),
    (('nob', 'sme'), u'leamaw'),
    (('nob', 'sme'), u'lege'),
    (('nob', 'sme'), u'leke'),
    (('nob', 'sme'), u'lese'),
    (('nob', 'sme'), u'ligge'),
    (('nob', 'sme'), u'ligger ved'),
    (('nob', 'sme'), u'liker ikke'),
    (('nob', 'sme'), u'liker'),
    (('nob', 'sme'), u'liten'),
    (('nob', 'sme'), u'liturgi'),
    (('nob', 'sme'), u'mandager'),
    (('nob', 'sme'), u'mat'),
    (('nob', 'sme'), u'men'),
    (('nob', 'sme'), u'menneske'),
    (('nob', 'sme'), u'mennesket'),
    (('nob', 'sme'), u'middag'),
    (('nob', 'sme'), u'mihkal sin mor heter'),
    (('nob', 'sme'), u'mis lea'),
    (('nob', 'sme'), u'multebær'),
    (('nob', 'sme'), u'multer'),
    (('nob', 'sme'), u'mye'),
    (('nob', 'sme'), u'måle'),
    (('nob', 'sme'), u'måned'),
    (('nob', 'sme'), u'måneder'),
    (('nob', 'sme'), u'møte verb'),
    (('nob', 'sme'), u'møte'),
    (('nob', 'sme'), u'natur'),
    (('nob', 'sme'), u'naturbruk'),
    (('nob', 'sme'), u'naturen'),
    (('nob', 'sme'), u'neste'),
    (('nob', 'sme'), u'nisse'),
    (('nob', 'sme'), u'noe'),
    (('nob', 'sme'), u'oeft'),
    (('nob', 'sme'), u'ofte'),
    (('nob', 'sme'), u'også'),
    (('nob', 'sme'), u'olje'),
    (('nob', 'sme'), u'om høsten'),
    (('nob', 'sme'), u'om sommeren'),
    (('nob', 'sme'), u'om vinteren'),
    (('nob', 'sme'), u'om'),
    (('nob', 'sme'), u'omsorgssenter'),
    (('nob', 'sme'), u'omtrent'),
    (('nob', 'sme'), u'onsdag'),
    (('nob', 'sme'), u'opp'),
    (('nob', 'sme'), u'opplegg'),
    (('nob', 'sme'), u'oppskrift'),
    (('nob', 'sme'), u'ost'),
    (('nob', 'sme'), u'ovdal'),
    (('nob', 'sme'), u'pappa'),
    (('nob', 'sme'), u'patent'),
    (('nob', 'sme'), u'pent'),
    (('nob', 'sme'), u'pepper'),
    (('nob', 'sme'), u'plass'),
    (('nob', 'sme'), u'plukke bær'),
    (('nob', 'sme'), u'postkontor'),
    (('nob', 'sme'), u'potte'),
    (('nob', 'sme'), u'purre'),
    (('nob', 'sme'), u'purreløk'),
    (('nob', 'sme'), u'på ordentlig'),
    (('nob', 'sme'), u'raring'),
    (('nob', 'sme'), u'regning'),
    (('nob', 'sme'), u'reise'),
    (('nob', 'sme'), u'renne'),
    (('nob', 'sme'), u'ri'),
    (('nob', 'sme'), u'riktig'),
    (('nob', 'sme'), u'rydde'),
    (('nob', 'sme'), u'sage'),
    (('nob', 'sme'), u'salat'),
    (('nob', 'sme'), u'salt'),
    (('nob', 'sme'), u'samboer'),
    (('nob', 'sme'), u'samisk'),
    (('nob', 'sme'), u'samtale'),
    (('nob', 'sme'), u'saus'),
    (('nob', 'sme'), u'sin'),
    (('nob', 'sme'), u'skatt'),
    (('nob', 'sme'), u'skatter'),
    (('nob', 'sme'), u'slutter'),
    (('nob', 'sme'), u'slå'),
    (('nob', 'sme'), u'som'),
    (('nob', 'sme'), u'sommer'),
    (('nob', 'sme'), u'spille'),
    (('nob', 'sme'), u'spilt'),
    (('nob', 'sme'), u'spise'),
    (('nob', 'sme'), u'stabble'),
    (('nob', 'sme'), u'stable'),
    (('nob', 'sme'), u'sted'),
    (('nob', 'sme'), u'sterk vind'),
    (('nob', 'sme'), u'stjele'),
    (('nob', 'sme'), u'stolt'),
    (('nob', 'sme'), u'stryk'),
    (('nob', 'sme'), u'sy'),
    (('nob', 'sme'), u'sytten'),
    (('nob', 'sme'), u'så'),
    (('nob', 'sme'), u'søster'),
    (('nob', 'sme'), u'ta'),
    (('nob', 'sme'), u'takstol'),
    (('nob', 'sme'), u'tar'),
    (('nob', 'sme'), u'tekst'),
    (('nob', 'sme'), u'telefonnummer'),
    (('nob', 'sme'), u'tidligere'),
    (('nob', 'sme'), u'tie'),
    (('nob', 'sme'), u'tilbe'),
    (('nob', 'sme'), u'tjuefjerde'),
    (('nob', 'sme'), u'tomat'),
    (('nob', 'sme'), u'tomatpure'),
    (('nob', 'sme'), u'trenge'),
    (('nob', 'sme'), u'trening'),
    (('nob', 'sme'), u'trivelig'),
    (('nob', 'sme'), u'tvinge'),
    (('nob', 'sme'), u'tysk'),
    (('nob', 'sme'), u'underholde'),
    (('nob', 'sme'), u'unge'),
    (('nob', 'sme'), u'vakker'),
    (('nob', 'sme'), u'vann'),
    (('nob', 'sme'), u'vant'),
    (('nob', 'sme'), u'vaske opp'),
    (('nob', 'sme'), u'vaske'),
    (('nob', 'sme'), u'ved siden av'),
    (('nob', 'sme'), u'vegg'),
    (('nob', 'sme'), u'veggeme'),
    (('nob', 'sme'), u'veggene'),
    (('nob', 'sme'), u'vegger'),
    (('nob', 'sme'), u'veidnes'),
    (('nob', 'sme'), u'veidnesklubben'),
    (('nob', 'sme'), u'veldig'),
    (('nob', 'sme'), u'venn'),
    (('nob', 'sme'), u'verden'),
    (('nob', 'sme'), u'vestavind'),
    (('nob', 'sme'), u'videregående skole'),
    (('nob', 'sme'), u'videregående'),
    (('nob', 'sme'), u'viessu'),
    (('nob', 'sme'), u'vind'),
    (('nob', 'sme'), u'vurdere'),
    (('nob', 'sme'), u'våkne'),
    (('nob', 'sme'), u'vår'),
    (('nob', 'sme'), u'å ha'),
    (('nob', 'sme'), u'å møte'),
    (('nob', 'sme'), u'økonomi'),
    (('sme', 'fin'), u'ahte'),
    (('sme', 'fin'), u'almmiguovlu'),
    (('sme', 'fin'), u'asia'),
    (('sme', 'fin'), u'bagadalli'),
    (('sme', 'fin'), u'bealljái'),
    (('sme', 'fin'), u'beasat'),
    (('sme', 'fin'), u'beassat'),
    (('sme', 'fin'), u'biegga'),
    (('sme', 'fin'), u'boagusta'),
    (('sme', 'fin'), u'boagustit'),
    (('sme', 'fin'), u'boahtin'),
    (('sme', 'fin'), u'botnje'),
    (('sme', 'fin'), u'buddáduvvat'),
    (('sme', 'fin'), u'buot'),
    (('sme', 'fin'), u'báhcit'),
    (('sme', 'fin'), u'coggat'),
    (('sme', 'fin'), u'dadjá'),
    (('sme', 'fin'), u'dalle'),
    (('sme', 'fin'), u'de'),
    (('sme', 'fin'), u'diibmu'),
    (('sme', 'fin'), u'doalli'),
    (('sme', 'fin'), u'dohpo'),
    (('sme', 'fin'), u'doppe'),
    (('sme', 'fin'), u'dovdat'),
    (('sme', 'fin'), u'dušše'),
    (('sme', 'fin'), u'dállu'),
    (('sme', 'fin'), u'dáppehan'),
    (('sme', 'fin'), u'ealli'),
    (('sme', 'fin'), u'eamidin'),
    (('sme', 'fin'), u'fadda'),
    (('sme', 'fin'), u'fas'),
    (('sme', 'fin'), u'fáippastit'),
    (('sme', 'fin'), u'gal'),
    (('sme', 'fin'), u'garra'),
    (('sme', 'fin'), u'geahčadit'),
    (('sme', 'fin'), u'giige'),
    (('sme', 'fin'), u'gitta'),
    (('sme', 'fin'), u'guovttos'),
    (('sme', 'fin'), u'gutna'),
    (('sme', 'fin'), u'gávdno'),
    (('sme', 'fin'), u'hutka'),
    (('sme', 'fin'), u'hutkat'),
    (('sme', 'fin'), u'hutkkálaš'),
    (('sme', 'fin'), u'háv'),
    (('sme', 'fin'), u'hávdádit'),
    (('sme', 'fin'), u'jienas'),
    (('sme', 'fin'), u'jietnadan'),
    (('sme', 'fin'), u'jođiheaddji'),
    (('sme', 'fin'), u'juo'),
    (('sme', 'fin'), u'juohke'),
    (('sme', 'fin'), u'juoidá'),
    (('sme', 'fin'), u'juos'),
    (('sme', 'fin'), u'juosat'),
    (('sme', 'fin'), u'kanssa'),
    (('sme', 'fin'), u'kirjoittaa'),
    (('sme', 'fin'), u'kirjottaa'),
    (('sme', 'fin'), u'lahkonit'),
    (('sme', 'fin'), u'leamaš'),
    (('sme', 'fin'), u'liegga'),
    (('sme', 'fin'), u'liikká'),
    (('sme', 'fin'), u'lomalla'),
    (('sme', 'fin'), u'mearkugohte'),
    (('sme', 'fin'), u'miessi'),
    (('sme', 'fin'), u'misiin'),
    (('sme', 'fin'), u'missä'),
    (('sme', 'fin'), u'mohkki'),
    (('sme', 'fin'), u'mojohallat'),
    (('sme', 'fin'), u'mot'),
    (('sme', 'fin'), u'muhto'),
    (('sme', 'fin'), u'muhtumis'),
    (('sme', 'fin'), u'máhta'),
    (('sme', 'fin'), u'máhttit'),
    (('sme', 'fin'), u'naba'),
    (('sme', 'fin'), u'nebe'),
    (('sme', 'fin'), u'njammat'),
    (('sme', 'fin'), u'nu'),
    (('sme', 'fin'), u'nuppis'),
    (('sme', 'fin'), u'oaidná'),
    (('sme', 'fin'), u'olbmot'),
    (('sme', 'fin'), u'olgeš'),
    (('sme', 'fin'), u'olu'),
    (('sme', 'fin'), u'orui'),
    (('sme', 'fin'), u'ovddabealde'),
    (('sme', 'fin'), u'ovddal'),
    (('sme', 'fin'), u'roava'),
    (('sme', 'fin'), u'ruovgat'),
    (('sme', 'fin'), u'ráfálaš'),
    (('sme', 'fin'), u'ráigánit'),
    (('sme', 'fin'), u'sevii'),
    (('sme', 'fin'), u'stivrejeaddji'),
    (('sme', 'fin'), u'suohkan'),
    (('sme', 'fin'), u'teapmi'),
    (('sme', 'fin'), u'vadjat'),
    (('sme', 'fin'), u'veahás'),
    (('sme', 'fin'), u'veaháš'),
    (('sme', 'fin'), u'viegahallat'),
    (('sme', 'fin'), u'vuollegis'),
    (('sme', 'fin'), u'vuollái'),
    (('sme', 'fin'), u'vuot'),
    (('sme', 'fin'), u'váldi'),
    (('sme', 'fin'), u'váldobargu'),
    (('sme', 'fin'), u'álddagas'),
    (('sme', 'fin'), u'álddu'),
    (('sme', 'fin'), u'áldu'),
    (('sme', 'fin'), u'čohka'),
    (('sme', 'fin'), u'čuhppe'),
    (('sme', 'fin'), u'čuččodit'),
    (('sme', 'fin'), u'čábbát'),
    (('sme', 'nob'), u'Eanet'),
    (('sme', 'nob'), u'algan'),
    (('sme', 'nob'), u'alggan'),
    (('sme', 'nob'), u'alggos'),
    (('sme', 'nob'), u'algit'),
    (('sme', 'nob'), u'almmuhangeasku'),
    (('sme', 'nob'), u'almmuhit'),
    (('sme', 'nob'), u'astat'),
    (('sme', 'nob'), u'astta'),
    (('sme', 'nob'), u'asttá'),
    (('sme', 'nob'), u'astá'),
    (('sme', 'nob'), u'beaivi'),
    (('sme', 'nob'), u'bearal'),
    (('sme', 'nob'), u'bearralat'),
    (('sme', 'nob'), u'bidjat'),
    (('sme', 'nob'), u'bihca'),
    (('sme', 'nob'), u'bihcabáhcahasaid'),
    (('sme', 'nob'), u'bija'),
    (('sme', 'nob'), u'boastakantuvra'),
    (('sme', 'nob'), u'bohccebiddji'),
    (('sme', 'nob'), u'bohttu'),
    (('sme', 'nob'), u'buozas'),
    (('sme', 'nob'), u'bágget'),
    (('sme', 'nob'), u'báhcahasaid'),
    (('sme', 'nob'), u'coggat'),
    (('sme', 'nob'), u'da lea'),
    (('sme', 'nob'), u'dat lea'),
    (('sme', 'nob'), u'deltaker'),
    (('sme', 'nob'), u'dette er'),
    (('sme', 'nob'), u'dette'),
    (('sme', 'nob'), u'diehttelas'),
    (('sme', 'nob'), u'dieva'),
    (('sme', 'nob'), u'diibmui'),
    (('sme', 'nob'), u'diibmuii'),
    (('sme', 'nob'), u'dine'),
    (('sme', 'nob'), u'dinet'),
    (('sme', 'nob'), u'dohkalaš'),
    (('sme', 'nob'), u'dohkkalaš'),
    (('sme', 'nob'), u'dohkket'),
    (('sme', 'nob'), u'dohkkálaš'),
    (('sme', 'nob'), u'dohkálaš'),
    (('sme', 'nob'), u'dolvo'),
    (('sme', 'nob'), u'duddjot'),
    (('sme', 'nob'), u'duhkoraddat'),
    (('sme', 'nob'), u'duhkordallat'),
    (('sme', 'nob'), u'dulka'),
    (('sme', 'nob'), u'duogábealde'),
    (('sme', 'nob'), u'duogáš'),
    (('sme', 'nob'), u'dáhpáhuvvat'),
    (('sme', 'nob'), u'dállu'),
    (('sme', 'nob'), u'eaibmi'),
    (('sme', 'nob'), u'favoriht'),
    (('sme', 'nob'), u'favorihtt'),
    (('sme', 'nob'), u'favorihtta'),
    (('sme', 'nob'), u'favorihttamusihkka'),
    (('sme', 'nob'), u'favoritt'),
    (('sme', 'nob'), u'feaskkir'),
    (('sme', 'nob'), u'ferdig'),
    (('sme', 'nob'), u'firon'),
    (('sme', 'nob'), u'fiskegrateng'),
    (('sme', 'nob'), u'fysioterapevta'),
    (('sme', 'nob'), u'garvodan'),
    (('sme', 'nob'), u'gaskabiebmu'),
    (('sme', 'nob'), u'gaskavahkku'),
    (('sme', 'nob'), u'gassada'),
    (('sme', 'nob'), u'geahpas'),
    (('sme', 'nob'), u'geahppa'),
    (('sme', 'nob'), u'geardi'),
    (('sme', 'nob'), u'girjerájus'),
    (('sme', 'nob'), u'goarrrut'),
    (('sme', 'nob'), u'goarrut'),
    (('sme', 'nob'), u'guite'),
    (('sme', 'nob'), u'gulaskuddan'),
    (('sme', 'nob'), u'gulaskuddat'),
    (('sme', 'nob'), u'guoibmi'),
    (('sme', 'nob'), u'guoika'),
    (('sme', 'nob'), u'gusta'),
    (('sme', 'nob'), u'guštá'),
    (('sme', 'nob'), u'gárggiideapmi'),
    (('sme', 'nob'), u'gárvodan'),
    (('sme', 'nob'), u'gárvodit'),
    (('sme', 'nob'), u'gávpi'),
    (('sme', 'nob'), u'heivemin'),
    (('sme', 'nob'), u'heivvemin'),
    (('sme', 'nob'), u'helmmot'),
    (('sme', 'nob'), u'hupmat'),
    (('sme', 'nob'), u'hálla'),
    (('sme', 'nob'), u'hállat'),
    (('sme', 'nob'), u'hápmá'),
    (('sme', 'nob'), u'hápmása'),
    (('sme', 'nob'), u'hápmásažžan'),
    (('sme', 'nob'), u'hárjánan'),
    (('sme', 'nob'), u'hárvenaš'),
    (('sme', 'nob'), u'i'),
    (('sme', 'nob'), u'idja'),
    (('sme', 'nob'), u'issorasat'),
    (('sme', 'nob'), u'iđitbiebmu'),
    (('sme', 'nob'), u'jaskkodit'),
    (('sme', 'nob'), u'jed'),
    (('sme', 'nob'), u'jeg'),
    (('sme', 'nob'), u'jente'),
    (('sme', 'nob'), u'juoga'),
    (('sme', 'nob'), u'juoidá'),
    (('sme', 'nob'), u'kirku'),
    (('sme', 'nob'), u'kylling'),
    (('sme', 'nob'), u'lahka'),
    (('sme', 'nob'), u'lahkai'),
    (('sme', 'nob'), u'laktása'),
    (('sme', 'nob'), u'laktásit'),
    (('sme', 'nob'), u'leamaš'),
    (('sme', 'nob'), u'leaš'),
    (('sme', 'nob'), u'lihkan'),
    (('sme', 'nob'), u'liibmet'),
    (('sme', 'nob'), u'lisster'),
    (('sme', 'nob'), u'logaldalli'),
    (('sme', 'nob'), u'luđiide'),
    (('sme', 'nob'), u'lágan'),
    (('sme', 'nob'), u'láhka'),
    (('sme', 'nob'), u'láhkai'),
    (('sme', 'nob'), u'mandager'),
    (('sme', 'nob'), u'maŋŋel'),
    (('sme', 'nob'), u'mohkki'),
    (('sme', 'nob'), u'mun'),
    (('sme', 'nob'), u'mánnodat'),
    (('sme', 'nob'), u'mánnu'),
    (('sme', 'nob'), u'mánáidgárdi'),
    (('sme', 'nob'), u'måle'),
    (('sme', 'nob'), u'målte'),
    (('sme', 'nob'), u'neaktit'),
    (('sme', 'nob'), u'nieida'),
    (('sme', 'nob'), u'nigát'),
    (('sme', 'nob'), u'niidii'),
    (('sme', 'nob'), u'nuollat'),
    (('sme', 'nob'), u'oadju'),
    (('sme', 'nob'), u'ohccis'),
    (('sme', 'nob'), u'ohcis'),
    (('sme', 'nob'), u'olggoš'),
    (('sme', 'nob'), u'olla'),
    (('sme', 'nob'), u'ollašuhttit'),
    (('sme', 'nob'), u'ollu'),
    (('sme', 'nob'), u'olmmoš'),
    (('sme', 'nob'), u'orbbeš'),
    (('sme', 'nob'), u'orda'),
    (('sme', 'nob'), u'ore'),
    (('sme', 'nob'), u'ovdal'),
    (('sme', 'nob'), u'ovdamus'),
    (('sme', 'nob'), u'rissegierragat'),
    (('sme', 'nob'), u'rivttes'),
    (('sme', 'nob'), u'ruhtaheađis'),
    (('sme', 'nob'), u'ruhtahoidu'),
    (('sme', 'nob'), u'ruhtahođis'),
    (('sme', 'nob'), u'sadji'),
    (('sme', 'nob'), u'sahet'),
    (('sme', 'nob'), u'salat'),
    (('sme', 'nob'), u'seaidni'),
    (('sme', 'nob'), u'seakka'),
    (('sme', 'nob'), u'skuohppu'),
    (('sme', 'nob'), u'smávis'),
    (('sme', 'nob'), u'spillet'),
    (('sme', 'nob'), u'spábbačiekčan'),
    (('sme', 'nob'), u'stoahkat'),
    (('sme', 'nob'), u'stresset'),
    (('sme', 'nob'), u'suoládit'),
    (('sme', 'nob'), u'sádjá'),
    (('sme', 'nob'), u'sádjái'),
    (('sme', 'nob'), u'sámegielgalba'),
    (('sme', 'nob'), u'sárgá'),
    (('sme', 'nob'), u'tienas'),
    (('sme', 'nob'), u'uhcci'),
    (('sme', 'nob'), u'ullu'),
    (('sme', 'nob'), u'unni'),
    (('sme', 'nob'), u'vahku'),
    (('sme', 'nob'), u'vai'),
    (('sme', 'nob'), u'valdit'),
    (('sme', 'nob'), u'vullojuvvon'),
    (('sme', 'nob'), u'vuortnuhit'),
    (('sme', 'nob'), u'vuovdnái'),
    (('sme', 'nob'), u'váibbas'),
    (('sme', 'nob'), u'válddahagas'),
    (('sme', 'nob'), u'váldit'),
    (('sme', 'nob'), u'Ávdnasat'),
    (('sme', 'nob'), u'Áđđestaddi'),
    (('sme', 'nob'), u'álgit'),
    (('sme', 'nob'), u'čeabetbáddi'),
    (('sme', 'nob'), u'čivga'),
    (('sme', 'nob'), u'čohkohallat'),
    (('sme', 'nob'), u'čohkun'),
    (('sme', 'nob'), u'čuohppat'),
    (('sme', 'nob'), u'čuojaha'),
    (('sme', 'nob'), u'čáppat'),
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
    ('sme', 'nob', u'mun', "Not generating from mini_paradigm",
     form_contains(set([u'munnje', u'mus', u'munin']))),

    ###  - A:
    ###     - http://localhost:5000/detail/sme/nob/ruoksat.json
    ###     - test that context is found as well as paradigm
    ###     - test that +Use/NGminip forms are not generated
    ('sme', 'nob', u'heittot', "Dialectical forms present",
     form_doesnt_contain(set([u"heittohat", u"heittohut", u"heittohit"]))),

    ###  - A + context="bivttas":  heittot
    ###     - http://localhost:5000/detail/sme/nob/heittot.html
    ('sme', 'nob', u'heittot', "Context missing",
     form_contains(set([u"heittogis"]))),

    ###  - A + context="báddi":  guhkki
    ###     - http://localhost:5000/detail/sme/nob/guhkki.html
    ('sme', 'nob', u'guhkki', "Context missing",
     form_contains(set([u"guhkes"]))),

    ###  - Num + context="gápmagat":  guokte
    ###     - http://localhost:5000/detail/sme/nob/guokte.html
    ('sme', 'nob', u'guokte', "Context missing",
     form_contains(set([u"guovttit"]))),

    ###  - N + illpl="no": eahketroađđi, sihkarvuohta, skuvlaáigi
    ('sme', 'nob', u'eahketroađđi', "Illative plural present",
     form_doesnt_contain(set([u'eahketrođiide']))),

    ###  - N Prop Sg: Norga, Ruoŧŧa
    ###     - http://localhost:5000/detail/sme/nob/Ruoŧŧa.html
    ('sme', 'nob', u'Ruoŧŧa', "Forms not generated",
     form_contains(set([u'Ruoŧa bokte', u'Ruŧŧii', u'Ruoŧas']))),

    ###  - N Prop Pl: Iččát
    ###     - <l pos="N" type="Prop" nr="Pl">Iččát</l>
    ('sme', 'nob', u'Iččát', "Forms not generated",
     form_contains(set([u'Iččáid bokte', u'Iččáide', u'Iččáin']))),
    ('sme', 'nob', u'mannat', "Forms not generated",
     form_contains(set([u'manan']))),
    ('sme', 'nob', u'deaivvadit', "Overgenerating forms",
     form_doesnt_contain(set([u'deaivvadan']))),
    ('sme', 'nob', u'girji',
     "Overgenerating forms. Possible tag filtration issue.",
     form_doesnt_contain(set([u'girjje']))),

    ###  - N
    ###    - <l pos="N" type="G3">sámeášši</l>
    ('sme', 'nob', u'sámeášši', "Forms not generated",
     form_contains(set([u'sámeášši', u'sámeáššái', u'sámeáššiiguin']))),

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
        """ Test that the basic idea of testing will work.
            If there's a problem here, this is a problem. ;)
        """
        lang_pair, form = wordforms_that_shouldnt_fail[0]

        base = '/%s/%s/' % lang_pair
        rv = self.app.post(
            base, data={
                'lookup': form,
            })

        assert 'sihke' in rv.data
        assert u'både' in rv.data.decode('utf-8')
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
    ('sme', 'nob', u'ruovttueana', "Not generating from mini_paradigm",
     form_contains(set([
         u'ruovttueanan',
     ]))),
]


class VMax(ParadigmGenerationTests):

    paradigm_generation_tests = vmax


class ParadigmSelectionTest(WordLookupTests):
    """ These are really only for testing specifics in the paradigm
    directory structure the code, and don't need to be run as generation
    as a whole is tested above.
    """

    def test_misc_paradigms(self):

        with self.current_app.app_context():
            from paradigms import ParadigmConfig
            lookups = self.current_app.morpholexicon.lookup('mannat', source_lang='sme', target_lang='nob') \
                      + self.current_app.morpholexicon.lookup(u'Ráisa', source_lang='sme', target_lang='nob') \
                      + self.current_app.morpholexicon.lookup(u'dálkkádagat', source_lang='sme', target_lang='nob') \
                      + self.current_app.morpholexicon.lookup(u'álgoálbmotášši', source_lang='sme', target_lang='nob') \
                      + self.current_app.morpholexicon.lookup(u'Dálmmát', source_lang='sme', target_lang='nob') \
                      + self.current_app.morpholexicon.lookup(u'Gállábártnit', source_lang='sme', target_lang='nob') \
                      + self.current_app.morpholexicon.lookup(u'Iččát', source_lang='sme', target_lang='nob')

            pc = self.current_app.morpholexicon.paradigms
            for node, analyses in lookups:
                print("Testing: ", node, analyses)
                print(pc.get_paradigm('sme', node, analyses, debug=True))
                print('--')
