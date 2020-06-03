import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from base64 import b64encode

env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

def fig2data_url(fig):
    io = BytesIO()
    fig.savefig(io, format="PNG")
    b64 = b64encode(io.getvalue())
    url = "data:{};base64,{}".format("image/png", b64.decode("ascii"))
    return url

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("outfile")
    parser.add_argument("-d", "--data_path", default="../data")
    args = parser.parse_args()

    flightdata = yaml.load(open(args.infile))
    bahamas_path = os.path.join(args.data_path,
                                "bahamas_{:%Y%m%d}_v0.4.nc".format(flightdata["date"]))
    dropsondes_path = os.path.join(args.data_path,
                                   "dropsondes_{:%Y%m%d}_v0.4.nc".format(flightdata["date"]))
    bahamas = xr.open_dataset(bahamas_path)
    dropsondes = xr.open_dataset(dropsondes_path)

    fig, ax = plt.subplots()
    ax.plot(bahamas.lon, bahamas.lat)
    im = fig2data_url(fig)
    plt.close("all")
    flightdata["plot_data"] = im

    for seg in flightdata["segments"]:
        sonde_mask = (dropsondes.launch_time.data >= np.datetime64(seg["start"])) \
                   & (dropsondes.launch_time.data < np.datetime64(seg["end"]))
        sondes = dropsondes.isel(sonde_number=sonde_mask)
        seg_bahamas = bahamas.sel(time=slice(seg["start"], seg["end"]))
        fig, ax = plt.subplots()
        ax.plot(seg_bahamas.lon, seg_bahamas.lat)
        sonde_track = bahamas.sel(time=sondes.launch_time, method="nearest")
        ax.scatter(sonde_track.lon, sonde_track.lat, color="C1")
        im = fig2data_url(fig)
        plt.close("all")
        seg["plot_data"] = im
        seg["sonde_count_in_data"] = len(sondes.launch_time)

    tpl = env.get_template("flight.html")

    with open(args.outfile, "w") as outfile:
        outfile.write(tpl.render(flight=flightdata))

if __name__ == "__main__":
    _main()
