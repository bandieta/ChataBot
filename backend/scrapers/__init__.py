from .metrohouse import scrape as scrape_metrohouse
from .rema import scrape as scrape_rema
from .realton import scrape as scrape_realton
from .truhome import scrape as scrape_truhome
from .indexo import scrape as scrape_indexo
from .ire import scrape_ire
from .wgn import scrape as scrape_wgn
from .kopalnia import scrape as scrape_kopalnia
from .base import Listing


def get_all_scrapers():
    return [
        scrape_metrohouse,
        scrape_rema,
        scrape_realton,
        scrape_truhome,
        scrape_indexo,
        lambda: scrape_ire("Łowcy Nieruchomości", "https://www.lowcynieruchomosci.pl"),
        lambda: scrape_ire("SCN", "https://www.scn.net.pl"),
        scrape_wgn,
        scrape_kopalnia,
    ]
