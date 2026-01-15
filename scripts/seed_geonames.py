import argparse
import csv
import io
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

from sqlmodel import Session, select
from sqlalchemy import text

repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from db import engine
from models import Country, City


COUNTRY_INFO_URL = "https://download.geonames.org/export/dump/countryInfo.txt"
CITIES_URL = "https://download.geonames.org/export/dump/cities15000.zip"


def download_text(url: str) -> str:
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8")


def download_zip(url: str) -> bytes:
    with urllib.request.urlopen(url) as resp:
        return resp.read()


def parse_countries(text: str):
    countries = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        code = parts[0].strip()
        name = parts[4].strip()
        if code:
            countries.append((code, name))
    return countries


def parse_cities(zipped: bytes):
    with zipfile.ZipFile(io.BytesIO(zipped)) as zf:
        names = [n for n in zf.namelist() if n.endswith(".txt")]
        if not names:
            raise RuntimeError("No cities file found in GeoNames zip")
        with zf.open(names[0]) as fh:
            text = io.TextIOWrapper(fh, encoding="utf-8")
            reader = csv.reader(text, delimiter="\t")
            for row in reader:
                if len(row) < 15:
                    continue
                name = row[1].strip()
                country_code = row[8].strip()
                try:
                    population = int(row[14])
                except ValueError:
                    population = 0
                if name and country_code:
                    yield country_code, name, population


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10, help="Top cities per country by population")
    args = parser.parse_args()

    countries_text = download_text(COUNTRY_INFO_URL)
    countries = parse_countries(countries_text)

    city_candidates: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for country_code, name, population in parse_cities(download_zip(CITIES_URL)):
        city_candidates[country_code].append((name, population))

    with Session(engine) as session:
        session.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('countries','id'), "
                "COALESCE((SELECT MAX(id) FROM countries), 1), true)"
            )
        )
        existing_countries = {c.code: c for c in session.exec(select(Country)).all()}
        for code, name in countries:
            if code in existing_countries:
                country = existing_countries[code]
                if country.name != name:
                    country.name = name
                    session.add(country)
            else:
                session.add(Country(code=code, name=name))
        session.commit()
        session.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('countries','id'), "
                "COALESCE((SELECT MAX(id) FROM countries), 1), true)"
            )
        )

        country_map = {c.code: c for c in session.exec(select(Country)).all() if c.code}

        existing_cities = session.exec(select(City)).all()
        existing_pairs = {(c.country_id, c.name) for c in existing_cities}

        inserts = 0
        session.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('cities','id'), "
                "COALESCE((SELECT MAX(id) FROM cities), 1), true)"
            )
        )
        for code, country in country_map.items():
            candidates = city_candidates.get(code, [])
            if not candidates:
                continue
            top_cities = sorted(candidates, key=lambda x: x[1], reverse=True)[: args.top]
            for name, _population in top_cities:
                key = (country.id, name)
                if key in existing_pairs:
                    continue
                session.add(City(country_id=country.id, name=name))
                inserts += 1
        session.commit()
        session.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('cities','id'), "
                "COALESCE((SELECT MAX(id) FROM cities), 1), true)"
            )
        )

    print(f"Seeded {len(countries)} countries and {inserts} cities (top {args.top} per country).")


if __name__ == "__main__":
    main()
