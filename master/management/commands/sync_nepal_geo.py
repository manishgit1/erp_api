import json
import urllib.request

from django.core.management.base import BaseCommand
from django.db import transaction

from master.models import GlobalProvince, GlobalDistrict, GlobalVdcMunicipality

DATA_URL = (
    "https://raw.githubusercontent.com/sagautam5/local-states-nepal/"
    "master/dataset/alldataset/en.json"
)

CATEGORY_SHORT_CODES = {
    1: "MC",   # Metropolitan City
    2: "SMC",  # Sub-Metropolitan City
    3: "M",    # Municipality
    4: "RM",   # Rural Municipality
}


def as_list(value):
    """The upstream dataset serializes some nested collections as JSON
    objects (keyed by string index) instead of arrays when the source
    PHP array wasn't 0-indexed contiguously. Normalize both to a list."""
    if isinstance(value, dict):
        return list(value.values())
    return value or []


class Command(BaseCommand):
    help = "Sync GlobalProvince/GlobalDistrict/GlobalVdcMunicipality from the public Nepal administrative divisions dataset"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url", default=DATA_URL,
            help="URL of the province/district/municipality JSON dataset to sync from",
        )

    def handle(self, *args, **options):
        url = options["url"]
        self.stdout.write(f"Fetching {url} ...")
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())

        stats = {"province": [0, 0], "district": [0, 0], "municipality": [0, 0]}

        with transaction.atomic():
            province_by_name = {}
            for p in as_list(data):
                obj, created = GlobalProvince.objects.update_or_create(
                    name=p["name"],
                    defaults={"alias": p["name"]},
                )
                province_by_name[p["name"]] = obj
                stats["province"][0 if created else 1] += 1

            district_by_name = {}
            for p in as_list(data):
                province_obj = province_by_name[p["name"]]
                for d in as_list(p["districts"]):
                    obj, created = GlobalDistrict.objects.update_or_create(
                        name=d["name"],
                        province=province_obj,
                        defaults={"alias": d["name"]},
                    )
                    district_by_name[d["name"]] = obj
                    stats["district"][0 if created else 1] += 1

            for p in as_list(data):
                for d in as_list(p["districts"]):
                    district_obj = district_by_name[d["name"]]
                    for m in as_list(d["municipalities"]):
                        short_code = CATEGORY_SHORT_CODES.get(m.get("category_id"), "")
                        _, created = GlobalVdcMunicipality.objects.update_or_create(
                            name=m["name"],
                            district=district_obj,
                            defaults={"alias": short_code or m["name"]},
                        )
                        stats["municipality"][0 if created else 1] += 1

        for label, (created, updated) in stats.items():
            self.stdout.write(self.style.SUCCESS(
                f"{label}: {created} created, {updated} updated"
            ))
