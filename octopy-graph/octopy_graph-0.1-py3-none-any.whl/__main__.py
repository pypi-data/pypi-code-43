# -*- coding: utf-8 -*-
"""Generate the graphs supported by the tool"""
from datetime import datetime, timedelta
import argparse
import sys

import octopy_graph as og


def get_parser():
    """The command line parser"""
    parser = argparse.ArgumentParser(description="GitDraw")
    parser.add_argument("-k", "--apikey", help="The API Key", required=True)
    parser.add_argument(
        "-g", "--gasserial", help="The gas meters serial number", required=True
    )
    parser.add_argument("-r", "--mprn", help="The gas meters MPRN", required=True)
    parser.add_argument(
        "-e",
        "--electricserial",
        help="The electricity meters serial number",
        required=True,
    )
    parser.add_argument(
        "-a", "--mpan", help="The electricity meters MPAN", required=True
    )
    return parser


def get_tool(key, gas_serial, elec_serial, mprn, mpan):
    """Get a MeterQueryTool"""
    g_meter = og.GasMeter(mprn, gas_serial)
    e_meter = og.ElectricityMeter(mpan, elec_serial)
    return og.MeterQueryTool(key, g_meter, e_meter)


def main():
    """Main program path"""
    parser = get_parser()
    args = parser.parse_args()
    tool = get_tool(
        args.apikey, args.gasserial, args.electricserial, args.mprn, args.mpan
    )

    fig1 = og.average_hourly_consumption(tool)
    fig2 = og.average_daily_consumption(tool)
    fig3 = og.average_weekly_consumption(tool)
    fig4 = og.daily_consumption(tool, datetime.now() - timedelta(days=1))
    fig5 = og.weekly_consumption(tool, datetime.now() - timedelta(days=7))

    fig1.show()
    fig3.show()
    fig2.show()
    fig4.show()
    fig5.show()


if __name__ == "__main__":
    sys.exit(main())
