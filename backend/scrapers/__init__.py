from .metrohouse import scrape as scrape_metrohouse
from .rema import scrape as scrape_rema
from .realton import scrape as scrape_realton
from .truhome import scrape as scrape_truhome
from .indexo import scrape as scrape_indexo
from .ire import scrape_ire
from .offer_card import scrape_offer_card
from .wgn import scrape as scrape_wgn
from .kopalnia import scrape as scrape_kopalnia
from .lukhouse import scrape as scrape_lukhouse
from .bestnest import scrape as scrape_bestnest
from .base import Listing


def get_all_scrapers():
    return [
        scrape_metrohouse,
        scrape_rema,
        scrape_realton,
        scrape_truhome,
        scrape_indexo,
        # IRE/OpenRem platform
        lambda: scrape_ire("Łowcy Nieruchomości", "https://www.lowcynieruchomosci.pl"),
        lambda: scrape_ire("SCN", "https://www.scn.net.pl"),
        lambda: scrape_ire("LIDER", "https://www.lider.tychy.pl", "/oferty/domy/"),
        lambda: scrape_ire("SALEX", "https://www.salex-nieruchomosci.pl", "/oferty/domy/"),
        lambda: scrape_ire("PROFEO", "https://www.profeocn.pl", "/oferty/domy/"),
        # offer-card platform
        lambda: scrape_offer_card("DOMEX", "https://www.dom-ex.pl"),
        lambda: scrape_offer_card("MLYNARSCY", "https://www.mlynarscy.com.pl"),
        lambda: scrape_offer_card("KAMA", "https://www.nieruchomoscikama.pl"),
        # individual scrapers
        scrape_wgn,
        scrape_kopalnia,
        scrape_lukhouse,
        scrape_bestnest,
    ]
