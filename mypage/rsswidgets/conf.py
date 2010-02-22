# -*- coding: utf-8 -*-

from mypage.utils.settings import Settings

CATEGORIES = (
    ('http://aktualne.centrum.cz/zahranici', { 'name': 'Zahraničí', 'url': 'http://www.aktualne.cz/zahranici/', }),
    ('http://aktualne.centrum.cz/ekonomika', { 'name': 'Ekonomika', 'url': 'http://www.aktualne.cz/ekonomika/', }),
    ('http://aktualne.centrum.cz/kultura',   { 'name': 'Kultura',   'url': 'http://www.aktualne.cz/kultura/', }),
    ('http://aktualne.centrum.cz/sportplus', { 'name': 'Sport',     'url': 'http://www.aktualne.cz/sport/', }),
    ('http://aktualne.centrum.cz/domaci',    { 'name': 'Domácí',    'url': 'http://www.aktualne.cz/domaci/', }),
    ('http://aktualne.centrum.cz/veda',      { 'name': 'Věda',      'url': 'http://www.aktualne.cz/veda/', }),
    ('http://aktualne.centrum.cz/priroda',   { 'name': 'Příroda',   'url': 'http://www.aktualne.cz/priroda/', }),

    ('http://aktualne.centrum.cz/zpravy/nehody',    { 'name': 'Nehody',    'url': 'http://www.aktualne.cz/zpravy/nehody/', }),
    ('http://aktualne.centrum.cz/zpravy/krimi',     { 'name': 'Krimi',     'url': 'http://www.aktualne.cz/zpravy/krimi/', }),
    ('http://aktualne.centrum.cz/zpravy/kuriozity', { 'name': 'Kuriozity', 'url': 'http://www.aktualne.cz/zpravy/kuriozity/', }),

    ('http://aktualne.centrum.cz/finance',   { 'name': 'Finance',   'url': 'http://www.aktualne.cz/finance/', }),
    ('http://bleskove.aktualne.centrum.cz',  { 'name': 'Celebrity', 'url': 'http://www.bleskove.cz/', }),

    ('http://zena.centrum.cz/moda-a-krasa',  { 'name': 'Móda a krása', 'url': 'http://www.zena.cz/moda-a-krasa/', }),

    ('http://spunt.centrum.cz', { 'name': 'Děti', 'url': 'http://www.spunt.cz/', }),

    ('http://zdravi.centrum.cz', { 'name': 'Zdraví', 'url': 'http://zdravi.centrum.cz/', }),
    ('http://utulne.centrum.cz', { 'name': 'Bydlení', 'url': 'http://utulne.centrum.cz/', }),

    ('http://zena.centrum.cz',               { 'name': 'Žena',      'url': 'http://www.zena.cz/', }),

    ('', { 'name': 'Zprávy', 'url': 'http://aktualne.centrum.cz', }),
)

DEFAULT_ITEM_COUNT = 8

settings = Settings('mypage.rsswidgets.conf')

