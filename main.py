import argparse
from datetime import date
from core.utils import valid_date
from dukascopy import fetch_ticks


def main():
    parser = argparse.ArgumentParser(prog='dukas', usage='%(prog)s [options]')
    parser.add_argument('symbols', metavar='N', type=str, nargs='+', help='symbol list using format EURUSD EURGBP')
    parser.add_argument('-d', '--day', type=valid_date,  help='specific day format YYYY-MM-DD (default today)', default=date.today())
    parser.add_argument('-s', '--startdate', type=valid_date,  help='start date format YYYY-MM-DD (default today)')
    parser.add_argument('-e', '--enddate', type=valid_date,  help='end date format YYYY-MM-DD (default today)')
    args = parser.parse_args()

    if args.startdate is not None:
        start = args.startdate
    else:
        start = args.day

    if args.enddate is not None:
        end = args.enddate
    else:
        end = args.day

    fetch_ticks(args.symbols, start, end)

if __name__ == '__main__':
    main()