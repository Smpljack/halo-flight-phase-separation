import ruamel.yaml

def _main():
    import argparse
    parser = argparse.ArgumentParser(description="""
attaches dropsonde ids to segment files

NOTE: the flight_segment file will be overwritten by this program.
""")
    parser.add_argument("flight_segment", help="flight info YAML file")
    parser.add_argument("sonde_info", help="sonde info YAML file")
    args = parser.parse_args()

    with open(args.flight_segment) as infile:
        flight = ruamel.yaml.load(infile, Loader=ruamel.yaml.RoundTripLoader)

    with open(args.sonde_info) as sondefile:
        sonde_info = ruamel.yaml.load(sondefile, Loader=ruamel.yaml.SafeLoader)

    if "platform" not in flight:
        print("ERROR: platform must be specified in flight file")
        return -1

    platform = flight["platform"]

    for seg in flight["segments"]:
        if "good_dropsondes" in seg:
            del seg["good_dropsondes"]
        sonde_ids = {
            flag: [s["sonde_id"]
                   for s in sonde_info
                   if s["platform"] == platform
                   and s["flag"] == flag
                   and s["launch_time"] >= seg["start"]
                   and s["launch_time"] < seg["end"]]
            for flag in ["GOOD", "BAD", "UGLY"]
        }
        seg["dropsondes"] = sonde_ids

    with open(args.flight_segment, "w") as outfile:
        ruamel.yaml.dump(flight, outfile, Dumper=ruamel.yaml.RoundTripDumper)

    return 0

if __name__ == "__main__":
    exit(_main())
