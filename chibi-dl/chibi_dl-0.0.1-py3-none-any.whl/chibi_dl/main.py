#!/usr/bin/env python3
import logging
import random
from argparse import ArgumentParser

from chibi.file import Chibi_path

from chibi_dl.site import Site


logger_formarter = '%(levelname)s %(name)s %(asctime)s %(message)s'


parser = ArgumentParser(
    description="descarga mangas", fromfile_prefix_chars='@'
)

parser.add_argument(
    "sites", nargs='+', metavar="site",
    help="urls de las series que se quieren descargar" )

parser.add_argument(
    "--user", '-u', dest="user", default="",
    help="usuario del sitio" )

parser.add_argument(
    "--password", '-p', dest="password", default="",
    help="contrasenna del sitio" )

parser.add_argument(
    "--resoulution", '-r', dest="quality", default=240, type=int,
    help="resolucion a descargar" )

parser.add_argument(
    "--only_print", dest="only_print", action="store_true",
    help="define si silo va a imprimir la lista de links o episodios"
)

parser.add_argument(
    "--only_links", dest="only_print_links", action="store_true",
    help="si se usa solo imprimira las urls"
)

parser.add_argument(
    "--random", dest="random", action="store_true",
    help="procesa las urls en un orden aleatorio"
)

parser.add_argument(
    "--log_level", dest="log_level", default="INFO",
    help="nivel de log",
)

parser.add_argument(
    "-o", "--output", type=Chibi_path, dest="download_path",
    help="ruta donde se guardara el video o manga" )


def main():
    args = parser.parse_args()
    logging.basicConfig( level=args.log_level, format=logger_formarter )
    site = Site(
        user=args.user, password=args.password,
        quality=args.quality )
    if args.random:
        random.shuffle( args.sites )
    site.append( *args.sites )

    if args.only_print:
        site.print( args.only_print_links )
    else:
        site.download( args.download_path )
