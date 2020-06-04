import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from io import BytesIO
from base64 import b64encode

border_time = np.timedelta64(3, "m")

color_before = "C2"
color_at = "C0"
color_after = "C3"
color_sonde = "C1"
color_connection = "gray"

env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

def fig2data_url(fig):
    io = BytesIO()
    fig.savefig(io, format="PNG", bbox_inches="tight")
    b64 = b64encode(io.getvalue())
    url = "data:{};base64,{}".format("image/png", b64.decode("ascii"))
    return url

def start_end_lims(bahamas):
    lat_min = min(*bahamas.lat.data[[0,-1]])
    lat_max = max(*bahamas.lat.data[[0,-1]])
    lon_min = min(*bahamas.lon.data[[0,-1]])
    lon_max = max(*bahamas.lon.data[[0,-1]])
    delta = ((lat_max - lat_min) ** 2 + (lon_max - lon_min) ** 2)**.5
    lat_center = (lat_min + lat_max) / 2
    lon_center = (lon_min + lon_max) / 2
    return (lat_center - delta, lat_center + delta), (lon_center - delta, lon_center + delta)

def default_segment_plot(seg, sonde_track, seg_before, seg_after):
    fig = plt.figure(figsize=(8, 5), constrained_layout=True)
    spec = gridspec.GridSpec(ncols=3, nrows=4, figure=fig)
    overview_ax = fig.add_subplot(spec[:, :2])
    alt_ax = fig.add_subplot(spec[0, 2])
    roll_ax = fig.add_subplot(spec[1, 2], sharex=alt_ax)
    pitch_ax = fig.add_subplot(spec[2, 2], sharex=alt_ax)
    yaw_ax = fig.add_subplot(spec[3, 2], sharex=alt_ax)

    overview_ax.plot(seg.lon, seg.lat, color=color_at, zorder=10)
    overview_ax.plot(seg_before.lon, seg_before.lat, color=color_before, alpha=.3, zorder=0)
    overview_ax.plot(seg_after.lon, seg_after.lat, color=color_after, alpha=.3, zorder=0)
    overview_ax.scatter(sonde_track.lon, sonde_track.lat, color=color_sonde, zorder=5)

    overview_ax.set_title("segment overview")
    overview_ax.set_xlabel("longitude [deg]")
    overview_ax.set_ylabel("latitude [deg]")

    for ax, var, unit in [(alt_ax, "altitude", "m"),
                          (roll_ax, "roll", "deg"),
                          (pitch_ax, "pitch", "deg"),
                          (yaw_ax, "heading", "deg")]:
        seg[var].plot(ax=ax, color=color_at, zorder=10)
        seg_before[var].plot(ax=ax, color=color_before, alpha=.3, zorder=0)
        seg_after[var].plot(ax=ax, color=color_after, alpha=.3, zorder=0)
        ax.set_title(var)
        ax.set_ylabel(unit)

    for ax in [alt_ax, roll_ax, pitch_ax]:
        plt.setp(ax.get_xticklabels(), visible=False)
        ax.set_xlabel("")

    return fig

def circle_detail_plot(seg, sonde_track, seg_before, seg_after):
    fig, zoom_ax = plt.subplots(1, figsize=(4,4), constrained_layout=True)
    zoom_ax.plot(seg.lon, seg.lat, "o-", color=color_at, zorder=10)
    zoom_ax.plot(seg_before.lon, seg_before.lat, "x-", color=color_before, alpha=.3, zorder=0)
    zoom_ax.plot(seg_after.lon, seg_after.lat, "x-", color=color_after, alpha=.3, zorder=0)
    zoom_ax.plot([seg_before.lon.data[-1], seg.lon.data[0]],
                 [seg_before.lat.data[-1], seg.lat.data[0]],
                 "--", color=color_connection, alpha=.3, zorder=0)
    zoom_ax.plot([seg.lon.data[-1], seg_after.lon.data[0]],
                 [seg.lat.data[-1], seg_after.lat.data[0]],
                 "--", color=color_connection, alpha=.3, zorder=0)

    zoom_ax.scatter(sonde_track.lon, sonde_track.lat, color=color_sonde, zorder=5)
    lat_lims, lon_lims = start_end_lims(seg)
    zoom_ax.set_xlim(*lon_lims)
    zoom_ax.set_ylim(*lat_lims)
    zoom_ax.set_aspect("equal")
    zoom_ax.set_title("zoom on circle ends")
    zoom_ax.set_xlabel("longitude [deg]")
    zoom_ax.set_ylabel("latitude [deg]")

    return fig

def straight_leg_detail_plot(seg, sonde_track, seg_before, seg_after):
    fig, (start_ax, end_ax) = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)

    start_lat, end_lat = seg.lat.data[[0, -1]]
    start_lon, end_lon = seg.lon.data[[0, -1]]

    for ax, lat, lon, name in [(start_ax, start_lat, start_lon, "start"),
                               (end_ax, end_lat, end_lon, "end")]:
        ax.plot(seg.lon, seg.lat, "o-", color=color_at, zorder=10)
        ax.plot(seg_before.lon, seg_before.lat, "x-", color=color_before, alpha=.3, zorder=0)
        ax.plot(seg_after.lon, seg_after.lat, "x-", color=color_after, alpha=.3, zorder=0)
        ax.scatter(sonde_track.lon, sonde_track.lat, color=color_sonde, zorder=5)

        ax.set_xlim(lon - .1, lon + .1)
        ax.set_ylim(lat - .1, lat + .1)
        ax.set_aspect("equal")
        ax.set_title("zoom on {}".format(name))
        ax.set_xlabel("longitude [deg]")
        ax.set_ylabel("latitude [deg]")

    return fig

def zoom_on(var, unit):
    def zoom_plot(seg, sonde_track, seg_before, seg_after):
        fig, (start_ax, end_ax) = plt.subplots(1, 2, figsize=(8,3), constrained_layout=True)

        tofs = np.timedelta64(30, "s")

        for ax, t, name in [(start_ax, seg.time.data[0], "start"),
                      (end_ax, seg.time.data[-1], "end")]:
            seg[var].plot(ax=ax, color=color_at, zorder=10)
            seg_before[var].plot(ax=ax, color=color_before, alpha=.3, zorder=0)
            seg_after[var].plot(ax=ax, color=color_after, alpha=.3, zorder=0)
            ax.set_title("zoom on {}".format(name))
            ax.set_ylabel("{} [{}]".format(var, unit))

            ax.set_xlim(t - tofs, t + tofs)

        return fig
    return zoom_plot

def timeline_of(var, unit):
    def plot(seg, sonde_track, seg_before, seg_after):
        fig, ax  = plt.subplots(1, 1, figsize=(8,3), constrained_layout=True)

        seg[var].plot(ax=ax, color=color_at, zorder=10)
        seg_before[var].plot(ax=ax, color=color_before, alpha=.3, zorder=0)
        seg_after[var].plot(ax=ax, color=color_after, alpha=.3, zorder=0)
        ax.set_title(var)
        ax.set_ylabel("{} [{}]".format(var, unit))

        return fig
    return plot

SPECIAL_PLOTS = {
    "circle": [circle_detail_plot, zoom_on("roll", "deg")],
    "straight_leg": [straight_leg_detail_plot, zoom_on("roll", "deg")],
    "radar_calibration_wiggle": [zoom_on("roll", "deg")],
    "radar_calibration_tilted": [zoom_on("roll", "deg")],
    "lidar_leg": [timeline_of("altitude", "m"), zoom_on("altitude", "m")],
}

def plots_for_kinds(kinds):
    return [default_segment_plot] + \
           [plot
            for kind in kinds
            for plot in SPECIAL_PLOTS.get(kind, [])]

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("outfile")
    parser.add_argument("-d", "--data_path", default="../data")
    args = parser.parse_args()

    flightdata = yaml.load(open(args.infile), Loader=yaml.SafeLoader)
    bahamas_path = os.path.join(args.data_path,
                                "bahamas_{:%Y%m%d}_v0.4.nc".format(flightdata["date"]))
    dropsondes_path = os.path.join(args.data_path,
                                   "dropsondes_{:%Y%m%d}_v0.4.nc".format(flightdata["date"]))
    bahamas = xr.open_dataset(bahamas_path)
    dropsondes = xr.open_dataset(dropsondes_path)

    global_warnings = []
    if "flight_id" in flightdata:
        flight_id = flightdata["flight_id"]
    else:
        flight_id = ""
        global_warnings.append("flight_id is missing")

    fig, ax = plt.subplots()
    ax.plot(bahamas.lon, bahamas.lat)
    im = fig2data_url(fig)
    plt.close("all")
    flightdata["plot_data"] = im

    for seg in flightdata["segments"]:
        sonde_mask = (dropsondes.launch_time.data >= np.datetime64(seg["start"])) \
                   & (dropsondes.launch_time.data < np.datetime64(seg["end"]))
        sondes = dropsondes.isel(sonde_number=sonde_mask)
        t_start = np.datetime64(seg["start"])
        t_end = np.datetime64(seg["end"])
        seg_bahamas = bahamas.sel(time=slice(t_start, t_end))
        seg_before = bahamas.sel(time=slice(t_start - border_time, t_start))
        seg_after = bahamas.sel(time=slice(t_end, t_end + border_time))
        sonde_track = bahamas.sel(time=sondes.launch_time, method="nearest")

        plot_data = []
        for plot in plots_for_kinds(seg.get("kinds", [])):
            plot_data.append(fig2data_url(
                plot(seg_bahamas, sonde_track, seg_before, seg_after)))
            plt.close("all")

        seg["plot_data"] = plot_data
        seg["sonde_count_in_data"] = len(sondes.launch_time)
        seg["sonde_times"] = sondes.launch_time.data

    flightdata["warnings"] = global_warnings

    tpl = env.get_template("flight.html")

    with open(args.outfile, "w") as outfile:
        outfile.write(tpl.render(flight=flightdata))

if __name__ == "__main__":
    _main()
