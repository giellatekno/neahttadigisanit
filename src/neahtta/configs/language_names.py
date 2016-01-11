# -*- encoding: utf-8 -*-
"""This handles language name translation, and ISO transforms. When
adding new languages for dictionaries, their names will need to appear
here; and when adding new languages as internationalisation languages,
their names will need to be here too.

1. NAMES - Pairs of ISOs and language names marked for translation, such
   that a line appears in each *.po file, where the names will be
   translated

2. LOCALISATION_NAMES_BY_LANGUAGE - Pairs of ISOs and language names in
   the language itself. These names will be used in the localisations menu on the site.

3. ISO_TRANSFORMS - sometimes ISOs need to be transformed between
   2-character format and 3-character format, so if a language has a
   2-character version, we need the other as well.

"""

from flask.ext.babel import lazy_gettext as _
NAMES = dict([
    # sanit
    ('sme', _(u"North Sámi")),
    ('se', _(u"North Sámi")),
    ('SoMe', _(u"North Sámi (#SoMe)")),
    ('en', _(u"English")),
    ('hun', _(u"Hungarian")),

    # baakoeh
    ('sma', _(u"South Sámi")),

    # kyv
    ('kpv', _(u"Komi")),
    ('kpvS', _(u"Komi")),
    ('udm', _(u"Udmurt")),
    ('udmM', _(u"Udmurt")),

    # sanat
    ('fkv', _(u"Kven")),
    ('olo', _(u"Olonetsian")),
    ('est', _(u"Estonian")),

    # sonad
    ('liv', _(u"Livonian")),
    ('livM', _(u"Livonian")),
    ('izh', _(u"Izhorian")),
    ('vep', _(u"Veps")),
    ('vro', _(u"Võro")),
    ('vot', _(u"Votic")),

    # valks
    ('myv', _(u"Erzya Mordvin")),
    ('mdf', _(u"Moksha")),
    ('fra', _(u"French")),
    ('deu', _(u"German")),

    # muter
    ('mrj', _(u"Western Mari")),
    ('mhr', _(u"Eastern Mari")),

    # vada
    ('yrk', _(u"Nenets")),

    # saan
    ('sms', _(u"Skolt Sami")),
    ('smsM', _(u"Skolt Sami")),

    # itwewina 
    ('crk', _(u"Plains Cree")),
    ('crkM', _(u"Plains Cree")),

    # dikaneisdi 
    ('chr', _(u"Cherokee")),
    ('chrL', _(u"Cherokee")),

    # guusaaw
    ('hdn', _(u"Northern Haida")),
    ('hdnM', _(u"Northern Haida")),

    # saanih
    ('smn', _(u"Inari Saami")),

    # ndstesting
    ('kca', _(u"Khanty")),
    # ndstesting
    ('gle', _(u"Irish")),

    # target languages
    ('fin', _(u"Finnish")),
    ('nob', _(u"Norwegian")),

    ('ru', _(u"Russian")),
    ('rus', _(u"Russian")),

    ('fi', _(u"Finnish")),
    ('no', _(u"Norwegian")),
    ('nob', _(u"Norwegian")),
    ('lv', _(u"Latvian")),
    ('lav', _(u"Latvian")),
    ('eng', _(u"English")),
    ('hdn', _(u"Haida")),
    ('fra', _(u"French")),
    ('deu', _(u"German")),
])

ISO_DISPLAY_RELABELS = dict([
    ('crk',      u'âêîô'),
    ('crk_Macr', u'āēīō'),
])

# These will show up in the localization menu, or wherever the
# language's own name needs to be visible. If the language
# also has a two-character ISO, that will need to be listed too.

LOCALISATION_NAMES_BY_LANGUAGE = dict([
    ('sme', u"Davvisámegiella"),
    ('se', u"Davvisámegiella"),
    ('sma', u"Åarjelsaemien gïele"),
    ('ru', u"Русский"),
    ('olo', u"Livvin kieli"),
    ('no', u"Norsk"),
    ('myv', u"Эрзянь кель"),
    ('mdf', u"Мокшень кяль"),
    ('mrj', u"Кырык мары йӹлмӹ"),
    ('yrk', u"Ненэцяʼ вада"),
    ('lv', u"Latviešu valoda"),
    ('lav', u"Latviešu valoda"),
    ('liv', u"Līvõ kēļ"),
    ('kpv', u"Коми кыв"),
    ('kv', u"Коми кыв"),
    ('kpvS', u"Коми кыв (Молодцов ортография)"),
    ('udm', u"Удмурт кыл"),
    ('izh', u"Ižoran keel"),
    ('fkv', u"Kveenin kieli"),
    ('fi', u"Suomi"),
    ('crk', u"nêhiyawêwin"),
    ('crk_Macr', u"nēhiyawēwin"),
    ('eng', u"English"),
    ('et', u"Eesti"),
    ('est', u"Eesti"),
    ('sms', u"sääʹmǩiõll"),
    ('smn', u'Anarâškielâ'),
    ('hdn', u"X̲aat Kíl"),
    ('hdnM', u"X̲aat Kíl"),
    ('en', u"English"),
    ('fr', u"Français"),
    ('hun', u"Magyar"),
    ('chr', u"ᏣᎳᎩ ᎦᏬᏂᎯᏍᏗ"),

    ('vep', u"Vepsän kel’"),
    ('vro', u"Võru keel"),
    ('vot', u"Vađđa ceeli "),

    ('deu', u"Deutsch"),

    # ndstesting
    ('kca', u"ханты ясаӈ"),
    ('gle', u"Gaeilge"),
])

# Only put the exceptional ISOs here
ISO_TRANSFORMS = dict([
    ('se', 'sme'),
    ('no', 'nob'),
    ('fi', 'fin'),
    ('en', 'eng'),
    ('et', 'est'),
    ('lv', 'lav'),
    ('en', 'eng'),
    ('fr', 'fra'),
    ('de', 'deu'),
    ('kv', 'kpv'),
    ('hu', 'hun'),
])
