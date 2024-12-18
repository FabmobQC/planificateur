import json
from typing import List, TypedDict


class BorderBox(TypedDict):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class ConfigOsmData(TypedDict):
    filename: str
    base_filename: str
    url: str
    bbox: BorderBox


class GtfsInfos(TypedDict):
    filename: str
    url: str
    is_manual_download: bool | None
    is_timezone_incorrect: bool | None


class ConfigGtfsData(TypedDict):
    timezone: str
    infos: List[GtfsInfos]


class Config(TypedDict):
    project_name: str
    osm_data: ConfigOsmData
    gtfs_data: ConfigGtfsData


def open_config(config_path: str) -> Config:
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
    return config
