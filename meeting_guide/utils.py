import json
import os
import re
import requests

from django.core.files import File
from django.conf import settings

from meeting_guide.models import Region


def get_geocode_address(full_address):
    """
    Given a full address, get the Google address information. Use a local cache.

    Returns `None` if Google doesn't return an address.
    """

    address_components = {}
    address_components["problem"] = "OK"

    cache_filename = (
        "meeting_guide_cache/" +
        re.sub("[^0-9a-zA-Z]+", "", full_address.lower().lstrip(" ")) +
        ".json"
    )

    address_components["cache_status"] = "MISS"

    if os.path.isfile(cache_filename):
        # grab the json from the cache
        with open(cache_filename, "r") as f:
            django_file = File(f)
            cached_json = django_file.read()

        try:
            # JSON is valid
            address_data = json.loads(cached_json)
            address_components["cache_status"] = "HIT"
        except json.JSONDecodeError:
            # Invalid JSON, delete the file, get on next run
            os.remove(cache_filename)
            address_components["cache_status"] = "INVALID"

    if address_components["cache_status"] != "HIT":
        payload = {
            "bounds": settings.GOOGLE_MAPS_API_BOUNDS,
            "key": settings.GOOGLE_MAPS_V3_APIKEY,
            "address": full_address.lstrip(" ").replace("'", ""),
        }
        # payload = {'key': API_KEY, 'address': full_address.lstrip(' ')}
        api_request_url = "https://maps.googleapis.com/maps/api/geocode/json"

        # Send the request to Google Maps
        r = requests.get(api_request_url, params=payload)
        address_data = r.json()

        # Write cache file if status == OK
        if address_data["status"] == "OK":
            with open(cache_filename, "w") as f:
                django_file = File(f)
                json.dump(address_data, django_file, indent=4, separators=(",", ": "))

    # We have the data in 'address_data', let's do something with
    # each address and the associated meeting information.
    # Test to see if LOCATION address exists. If so, return the id from MySQL
    if address_data["status"] == "ZERO_RESULTS":
        address_components[
            "problem"
        ] = 'Google returned "ZERO_RESULTS" for address {0}:\n{1}\n\n.'.format(
            full_address, address_components
        )
    elif address_data["status"] == "OVER_QUERY_LIMIT":
        address_components[
            "problem"
        ] = 'Google returned "OVER_QUERY_LIMIT"; have we hit the API too much?'
    else:
        address_components["formatted_address"] = address_data["results"][0][
            "formatted_address"
        ]

        for address_component in address_data["results"][0]["address_components"]:
            for address_component_type in address_component["types"]:
                address_components[address_component_type] = address_component[
                    "short_name"
                ]

        address_components["lat"] = address_data["results"][0]["geometry"]["location"][
            "lat"
        ]
        address_components["lng"] = address_data["results"][0]["geometry"]["location"][
            "lng"
        ]

        if (
            "street_number" not in address_components or
            "route" not in address_components
        ):
            address_components[
                "problem"
            ] = 'Google did not return "street_number" or "route" for address {0}:\n{1}\n\n.'.format(
                full_address, address_components
            )
        else:
            address_components["full_address"] = (
                address_components["street_number"] + " " + address_components["route"]
            )

            #
            # This address is missing an administrative_area_level_2 reported here:
            # https://code.google.com/p/gmaps-api-issues/issues/detail?id=11492&thanks=11492&ts=1487542697
            #
            if "administrative_area_level_2" in address_components:
                address_components["region"] = address_components[
                    "administrative_area_level_2"
                ]
            else:
                address_components[
                    "problem"
                ] = 'Google did not return "administrative_area_level_2" (county / parish) for address {0}:\n{1}\n\n.'.format(
                    full_address, address_components
                )
                address_components["region"] = ""

            # Subregion: most granular to least granular
            if "neighborhood" in address_components:
                address_components["subregion"] = address_components["neighborhood"]
            elif "sublocality" in address_components:
                address_components["subregion"] = address_components["sublocality"]
            elif "locality" in address_components:
                address_components["subregion"] = address_components["locality"]
            elif "administrative_area_level_3" in address_components:
                address_components["subregion"] = address_components[
                    "administrative_area_level_3"
                ]
            elif "city" in address_components:
                address_components["subregion"] = address_components["city"]
            else:
                address_components["subregion"] = ""
                address_components[
                    "problem"
                ] = 'Google did not return "neighborhood", "locality", "sublocality", "city", or "administrative_area_level_3" for subregion field for address {0}:\n{1}\n\n.'.format(
                    full_address, address_components
                )

            # City: least granular below the county level
            if "city" in address_components:
                address_components["city"] = address_components["city"]
            elif "administrative_area_level_3" in address_components:
                address_components["city"] = address_components[
                    "administrative_area_level_3"
                ]
            elif "locality" in address_components:
                address_components["city"] = address_components["locality"]
            elif "sublocality" in address_components:
                address_components["city"] = address_components["sublocality"]
            elif "neighborhood" in address_components:
                address_components["city"] = address_components["neighborhood"]
            else:
                address_components["city"] = ""
                address_components[
                    "problem"
                ] = 'Google did not return "neighborhood", "locality", "city", or "administrative_area_level_3" for city field for address {0}:\n{1}\n\n.'.format(
                    full_address, address_components
                )

    return address_components


def build_tree(regions):
    """ Build up our regions recursively """
    items = []
    for r in regions:
        item = {
            "label": r.name,
            "value": r.id,
            "children": []
        }

        if r.children.count():
            item["children"] = build_tree(r.children.all())

        items.append(item)

    return items


def get_region_tree():
    """
    Generate deeply nested region data for use by react-dropdown-tree-select
    This returns a nested structure of lists and dicts of regions with their
    names, ids, and children.
    """
    top_regions = Region.objects.filter(parent__isnull=True).prefetch_related("children")
    return build_tree(top_regions)
