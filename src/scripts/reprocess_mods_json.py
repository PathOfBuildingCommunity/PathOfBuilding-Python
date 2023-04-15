"""
Reprocess base_items.json into a smaller file with only relevant items
base_items.json and mods.json come from https://github.com/brather1ng/RePoE/tree/master/RePoE/data
    and are not included in the git repo

"""
from pathlib import Path
import json


def read_json(filename):
    """
    Reads a json file
    :param filename: Name of xml to be read
    :returns: A dictionary of the contents of the file
    """
    _fn = Path(filename)
    if _fn.exists():
        try:
            with _fn.open("r") as json_file:
                _dict = json.load(json_file)
                return _dict
        except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
            print(f"Unable to open {_fn}")
    return None


def write_json(filename, _dict):
    """
    Write a json file
    :param filename: Name of json to be written
    :param _dict: New contents of the file
    :returns: N/A
    """
    _fn = Path(filename)
    try:
        with _fn.open("w") as json_file:
            json.dump(_dict, json_file, indent=4)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        print(f"Unable to write to {_fn}")


def trim_stats_list(_stats):
    """

    :param _stats:
    :return:
    """


def update_mod_name_with_numbers(_stat, _min, _max):
    """

    :param _stat:
    :param _min:
    :param _max:
    :return:
    """
    if _stat["index_handlers"]:
        # print(stat["index_handlers"][0],_min, _max)
        match stat["index_handlers"][0]:
            case "negate":
                _min, _max = 0 - _max, 0 - _min
            case "negate_and_double":
                _min, _max = 0 - (_max * 2), 0 - (_min * 2)
            case "double":
                _min, _max = _min * 2, _max * 2
            case "per_minute_to_per_second_2dp_if_required":
                _min, _max = _min / 60, _max / 60
        # print(stat["index_handlers"][0],_min, _max)

    # _format = _negative and "-" or _format
    _min_str = f"{_min}".replace(".0", "")
    _max_str = f"{_max}".replace(".0", "")
    if _min != _max:
        numbers = f'{_format}({_min_str}-{_max_str})'
    else:
        numbers = f'{_format}{_max_str}'
    if "{0} to {1}" in _stat["name"]:
        _stat["name"] = _stat["name"].replace("{0}", f"{_format}{_min_str}").replace("{1}", f"{_format}{_max_str}")
    else:
        _stat["name"] = _stat["name"].replace("{0}", numbers)
    _stat["min"], _stat["max"] = _min, _max


types_not_wanted = (
    "bestiary",
    "blight",
    "blight_tower",
    "bloodlines",
    "delve_area",
    "enchantment",
    "essence",
    "nemesis",
    "scourge_gimmick",
    "talisman",
    "torment",
    "unique",
)

# The dictionary we will build
item_mods = {}
jewels_mods = {}
abyss_jewels_mods = {}

# The dictionary of the incoming json
mods_json = read_json("mods.json")
stat_names_json = read_json("stat_translations.json")
# dictionary lookup for stat names
stat_names = {}

for stat in stat_names_json:
    # print(type(stat), stat)
    # print(type(stat), stat["English"])
    ids = stat["ids"]
    # print(f'\n ids:{len(ids)}, #English: {len(stat["English"])}', stat["English"])
    # print("\n", ids)
    for _id_idx in range(len(ids)):
        _id = stat["ids"][_id_idx]
        stat_names[_id] = []
        for _stat_idx in range(len(stat["English"])):
            _stat = stat["English"][_stat_idx]
            new_stat = {
                "name": _stat["string"],
                "format": _stat["format"][_id_idx],
                "condition": _stat["condition"][_id_idx],
                "index_handlers": _stat["index_handlers"][_id_idx],
            }
            stat_names[_id].append(new_stat)
            # print(stat_names[_id])

# temporary so i can see what i have
# write_json("New_stat_names.json", stat_names)

lines = []
for item_id in mods_json:
    if "map" in item_id.lower():
        continue
    dump = False
    for test in ("Expedition", "Heist", "Jun", "Monster", "PvP"):
        if item_id.startswith(test):
            dump = True
            break
    if dump:
        continue
    # if item_id != "AdditionalArrowInfluence1":
    #     continue
    mod = mods_json[item_id].copy()
    if len(mod["stats"]) != 1:
        print("\n", item_id, len(mod["stats"]))
        for stat in mod["stats"]:
            print(stat)

    generation_type = mod["generation_type"]
    if generation_type in types_not_wanted:
        # ignore
        continue
    mod["type"] = generation_type
    del mod["generation_type"]
    mod["affix"] = mod["name"]
    del mod["name"]

    # spawn_weights
    new_sw = {}
    dump = False
    for sw in mod["spawn_weights"]:
        new_sw[sw["tag"]] = sw["weight"]
        if "map" in sw["tag"]:
            dump = True
            break
    if dump:
        continue
    del mod["spawn_weights"]
    mod["spawn_weights"] = new_sw

    # Join the stats to the main mod list
    for stats in mod["stats"]:
        if stats["id"] == "dummy_stat_display_nothing":
            continue
        # print("stats", type(stats), stats)
        # get the stats from stat_translations
        stat_name = stat_names.get(stats["id"], None)
        # print("stat_name", type(stat_name), stat_name)
        # there are stats like 'local_influence_mod_requires_celestial_boss_presence', that do not need to be processed
        if stat_name is None:
            continue
        # print(item_id, len(stat_name))

        # process each stat, dumping anything we don't like
        new_stats = []
        for stat_idx in range(len(stat_name)):
            stat = stat_name[stat_idx].copy()
            # print(type(stat), stat)

            _min = stats["min"]
            _max = stats["max"]
            if _min == _max == 0:
                continue

            # get format without the # so it will '', '+' or 'ignore'
            _format = stat["format"].replace("#", "")
            # if _format == "ignore":
            #     print(item_id, stat_name)
            condition = stat["condition"]
            cond_max = condition.get("max", None)
            if _format == "ignore" and condition == {}:
                if _min == _max == len(stat_name) == 1:
                    update_mod_name_with_numbers(_stat, _min, _max)
                    new_stats.append(stat)
                    continue
                else:
                    # if condition == {} or (cond_max is not None and cond_max < stats["max"]):
                    if cond_max is not None and cond_max < stats["max"]:
                        continue
                #     print("\n", item_id, len(stat_name), "\n", mod, "\n" )
                #     for stat in stat_name:
                #         print(stat)

            # print(stat["name"])
            update_mod_name_with_numbers(_stat, _min, _max)
            new_stats.append(stat)

            if "EldritchImplicitPinnaclePresence" in item_id.lower():
                stat["name"] = f'While a Pinnacle Atlas Boss is in your Presence, {stat["name"]}'
            if "EldritchImplicitUniquePresence" in item_id.lower():
                stat["name"] = f'While a Unique Enemy is in your Presence, {stat["name"]}'

        if len(new_stats) > 1:
            tmp_new_stats = new_stats
            for idx in reversed(range(len(tmp_new_stats))):
                if tmp_new_stats[idx]["min"] < 0:
                    del new_stats[idx]
                elif "{1}" in tmp_new_stats[idx]["name"]:
                    del new_stats[idx]

        # When there are two stats, try to guess correctly which to remove
        # try to find a stat with an empty condition or condition["max"] == -1. Delete that one
        if len(new_stats) == 2:
            # print("\n", item_id)
            # for stat in new_stats:
            #     print(stat)
            condition = new_stats[0]["condition"]
            cond_max = condition.get("max", None)
            idx = 1
            if condition == {} or (cond_max is not None and cond_max < stats["max"]):
                idx = 0
            # print("idx", idx)
            del new_stats[idx]

        if len(new_stats) == 0:
            continue

        # error checking. if it prints somethiong went wrong
        # if len(new_stats) != 1:
        #     print("\n", item_id, len(new_stats))
        #     for stat in new_stats:
        #         print(stat)

        if mod["domain"] != "abyss_jewel":
            lines.append(f"{item_id},{new_stats[0]['name']}")

        stats["stats"] = new_stats
        stats["orig_stats"] = stat_name
        # print(type(stats), stats)

    # print(stat_names_json[item_id][0])
    if mod["domain"] == "abyss_jewel":
        abyss_jewels_mods[item_id] = mod
    else:
        item_mods[item_id] = mod

write_json("New_mods.json", item_mods)
# write_json("New_jewels.json", abyss_jewels_mods)
# write_json("New_mods_abyss_jewels.json", abyss_jewels_mods)

# with open('mods.txt', 'w') as f:
#     f.write('\n'.join(lines))

# EldritchImplicitPinnaclePresence
# "While a Pinnacle Atlas Boss is in your Presence,

# EldritchImplicitUniquePresence
# "While a Unique Enemy is in your Presence, "
