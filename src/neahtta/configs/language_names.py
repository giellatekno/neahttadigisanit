# -*- encoding: utf-8 -*-
# This is a temporary solution until I figure out the right way of
# getting Babel to compile strings out of app.config.yaml

# Here are all the names of the languages used in dictionaries, for
# internationalization.
from flaskext.babel import lazy_gettext as _
NAMES = dict([
    # sanit
    ('sme', _(u"North Sámi")),
    ('se', _(u"North Sámi")),
    ('SoMe', _(u"North Sámi (#SoMe)")),
    ('en', _(u"English")),

    # baakoeh
    ('sma', _(u"South Sámi")),

    # kyv
    ('kpv', _(u"Komi")),

    # sanat
    ('fkv', _(u"Kven")),
    ('liv', _(u"Livonian")),
    ('olo', _(u"Olonetsian")),
    ('izh', _(u"Izhorian")),
    ('est', _(u"Estonian")),

    # valks
    ('myv', _(u"Erzya Mordvin")),
    ('mdf', _(u"Moksha")),
    ('fra', _(u"French")),

    # muter
    ('mrj', _(u"Western Mari")),
    ('mhr', _(u"Eastern Mari")),

    # vada
    ('yrk', _(u"Nenets")),

    # saan
    ('sms', _(u"Skolt Sámi")),

    # pikiskwewina
    ('crk', _(u"Plains Cree")),

    # guusaaw
    ('hdn', _(u"Northern Haida")),

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
])

LOCALISATION_NAMES_BY_LANGUAGE = dict([
    # TODO: where I was unsure about language names, I included some
    # form of "kieli", so, someone should check what the common practice
    # is amongst these language groups.
    ('sme', u"Davvisámegiella"),
    ('se', u"Davvisámegiella"),
    ('sma', u"Åarjelsaemien gïele"),
    ('ru', u"Руский"),
    ('olo', u"Livvin kieli"), # TODO: flag
    ('no', u"Norsk"),
    ('myv', u"Эрзянь кель"),
    ('mdf', u"Мокшень кяль"), # TODO: flag
    ('mrj', u"Кырык мары йӹлмӹ"), # TODO: flag
    ('yrk', u"Ненэць вада"),
    ('lv', u"Latviešu valoda"),
    ('lav', u"Latviešu valoda"),
    ('liv', u"Līvõ kēļ"), # TODO: flag
    ('kpv', u"Коми кыв"), # TODO: flag
    ('izh', u"Ižoran keel"), # TODO: flag
    ('fkv', u"Kveenin kieli"), # TODO: flag
    ('fi', u"Suomi"),
    ('eng', u"English"),
    ('est', u"Estonian"), # TODO: flag
    ('sms', u"sääˊmǩiõll"),
    ('hdn', u"X̲aat Kíl"),
    ('en', u"English"),
    ('en', u"Français"),
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
])
