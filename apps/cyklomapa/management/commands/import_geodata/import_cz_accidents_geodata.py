#!/usr/bin/env python

"""
Download and extract Czechia accidents csv files

Functions:
 - import_cz_accidents_geodata::get_data_from_actual_year
 - import_cz_accidents_geodata::get_data_to_actual_year
"""

import datetime
import os
import pathlib
import ssl
import subprocess
import tempfile
import urllib

from bs4 import BeautifulSoup

ACCIDENT_DATA_FROM = 2016
ACCIDENT_CSV_FILE = "/tmp/result.csv"
BASE_URL = "https://www.policie.cz/"
ACCIDENTS_DATA_URL = f"{BASE_URL}clanek/statistika-nehodovosti-900835.aspx"


def set_lower_cipher_security():
    """Set lower TLS cipher security

    Fix error message (get data from 'https://www.policie.cz' server):

    'ssl.SSLError: [SSL: DH_KEY_TOO_SMALL] dh key too small (_ssl.c:852'
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.set_ciphers("DEFAULT@SECLEVEL=1")
    return context


def is_actual_prevous_month(filename):
    """Check if downloaded RAR archive with CSV files are from actual
    prevoius month (actual year)

    :param str filenam: RAR archive filename

    :return bool: True if data is from actual previous month
    """
    actual_previous_month = datetime.datetime.now().month - 1
    for s in filename.split("-"):
        try:
            if int(s) == actual_previous_month:
                return True
        except ValueError:
            pass


def download_and_extract_archive(url, output_filepath, count):
    """Download and extract RAR archive (CSV data)

    :param str url: RAR archive url
    :param str output_filepath: output RAR archive file path
    :param int count: counter for create unique dir where RAR archive
    will be extracted
    """
    response = urllib.request.urlopen(
        url=url, context=set_lower_cipher_security(),
    )
    with open(output_filepath, 'wb') as f:
        f.write(response.read())
    ext_dir = f"ext_{count}"
    os.mkdir(ext_dir)
    subprocess.call(["unrar", "e", f"{output_filepath}", f"{ext_dir}"])


def get_accident_data_page_soup():
    """Get accident data page soup

    :return obj: BeautifulSoup instance
    """
    return BeautifulSoup(
        urllib.request.urlopen(
            url=ACCIDENTS_DATA_URL,
            context=set_lower_cipher_security(),
        ),
        features="html.parser")


def get_data_from_actual_year(temp_dir, actual_previous_month_only=False):
    """Get data from actual year

    :param bool actual_previous_month_only: get actual previous month data
    :param str temp_dir: temporary directory path
    """
    soup = get_accident_data_page_soup()
    content_div = soup.find("div", {"id": "content"})
    download_dir = pathlib.Path(temp_dir) / str(datetime.datetime.now().year)

    os.mkdir(download_dir)
    os.chdir(download_dir)
    count = 0

    for i in content_div.find("table").find_all("a"):
        if "rar" in i.attrs["href"]:
            filename = pathlib.Path(i.attrs["href"]).stem
            filepath = download_dir / filename
            if actual_previous_month_only:
                if is_actual_prevous_month(filename):
                    download_and_extract_archive(
                        url=f"{BASE_URL}{i.attrs['href']}",
                        output_filepath=filepath, count=count)
                    break
            else:
                download_and_extract_archive(
                    url=f"{BASE_URL}{i.attrs['href']}",
                    output_filepath=filepath, count=count)
                count += 1


def get_data_to_actual_year(temp_dir):
    """Get accidents data from {ACCIDENT_DATA_FROM} to the actual year
    (including)

    :param str temp_dir: temporary directory path
    """
    soup = get_accident_data_page_soup()
    accidents_enties_sorted_by_year_div = soup.find("div", {"class": "in"})

    for i in accidents_enties_sorted_by_year_div.find_all("a"):
        if int(i.text) >= ACCIDENT_DATA_FROM:
            download_dir = pathlib.Path(temp_dir) / i.text
            os.mkdir(download_dir)
            os.chdir(download_dir)
            url = f"{BASE_URL}{i.attrs['href']}"
            page = urllib.request.urlopen(
                url=url,
                context=set_lower_cipher_security(),
            )
            soup = BeautifulSoup(page, features="html.parser")
            content_div = soup.find("div", {"id": "content"})
            for t in content_div.find_all("table"):
                count = 0
                for i in t.find_all("a"):
                    if ("rocenka" not in i.attrs["href"] and
                        "prehled" not in i.attrs["href"] and
                        "rar" in i.attrs["href"]):
                        filename = pathlib.Path(
                            i.attrs["href"]).stem
                        filepath = download_dir / filename
                        download_and_extract_archive(
                            url=f"{BASE_URL}{i.attrs['href']}",
                            output_filepath=filepath, count=count)
                        count += 1


def get_accident_data(output_csv_file, output_sqlite_db_file, temp_dir,
                      actual_previous_month_only=False):
    """Get Czechia accidents data

    :param str output_csv_file: out result CSV file
    :param str output_sqlite_db_file: out result Sqlite DB file
    :param str temp_dir: temporary directory path
    :param bool actual_previous_month_only: if True only actual previous
    month data will be imported
    """
    parse_accident_data_sh_script = (pathlib.Path(__file__).parent /
                                     "parse_czechia_accidents_data.sh")

    get_data_from_actual_year(
        temp_dir=temp_dir,
        actual_previous_month_only=actual_previous_month_only,
    )
    if not actual_previous_month_only:
        get_data_to_actual_year(temp_dir=temp_dir)
    os.chdir(parse_accident_data_sh_script.parent)

    subprocess.call([
        parse_accident_data_sh_script.resolve(),
        temp_dir,
        output_csv_file,
        output_sqlite_db_file,
    ])
