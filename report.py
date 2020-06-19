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
color_connection = "gray"

sonde_styles = {
    "GOOD": {"color": "green", "marker": "o"},
    "BAD": {"color": "red", "marker": "s"},
    "UGLY": {"color": "orange", "marker": "d"},
}

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

def plot_sondes(ax, sonde_tracks_by_flag, **kwargs):
    for flag, style in sonde_styles.items():
        if flag in sonde_tracks_by_flag:
            t = sonde_tracks_by_flag[flag]
            ax.scatter(t.lon, t.lat, **kwargs, **style)

def default_segment_plot(seg, sonde_tracks_by_flag, seg_before, seg_after):
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

    plot_sondes(overview_ax, sonde_tracks_by_flag, zorder=5)

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

def circle_detail_plot(seg, sonde_tracks_by_flag, seg_before, seg_after):
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

    plot_sondes(zoom_ax, sonde_tracks_by_flag, zorder=5)
    lat_lims, lon_lims = start_end_lims(seg)
    zoom_ax.set_xlim(*lon_lims)
    zoom_ax.set_ylim(*lat_lims)
    zoom_ax.set_aspect("equal")
    zoom_ax.set_title("zoom on circle ends")
    zoom_ax.set_xlabel("longitude [deg]")
    zoom_ax.set_ylabel("latitude [deg]")

    return fig

def straight_leg_detail_plot(seg, sonde_tracks_by_flag, seg_before, seg_after):
    fig, (start_ax, end_ax) = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)

    start_lat, end_lat = seg.lat.data[[0, -1]]
    start_lon, end_lon = seg.lon.data[[0, -1]]

    for ax, lat, lon, name in [(start_ax, start_lat, start_lon, "start"),
                               (end_ax, end_lat, end_lon, "end")]:
        ax.plot(seg.lon, seg.lat, "o-", color=color_at, zorder=10)
        ax.plot(seg_before.lon, seg_before.lat, "x-", color=color_before, alpha=.3, zorder=0)
        ax.plot(seg_after.lon, seg_after.lat, "x-", color=color_after, alpha=.3, zorder=0)
        plot_sondes(ax, sonde_tracks_by_flag, zorder=5)

        ax.set_xlim(lon - .1, lon + .1)
        ax.set_ylim(lat - .1, lat + .1)
        ax.set_aspect("equal")
        ax.set_title("zoom on {}".format(name))
        ax.set_xlabel("longitude [deg]")
        ax.set_ylabel("latitude [deg]")

    return fig

def zoom_on(var, unit, tofs=np.timedelta64(30, "s")):
    def zoom_plot(seg, sonde_tracks_by_flag, seg_before, seg_after):
        fig, (start_ax, end_ax) = plt.subplots(1, 2, figsize=(8,3), constrained_layout=True)

        tofs2 = tofs + np.timedelta64(1, "s")

        for ax, t, name in [(start_ax, seg.time.data[0], "start"),
                            (end_ax, seg.time.data[-1], "end")]:
            ts = slice(t - tofs2, t + tofs2)
            s1 = seg[var].sel(time=ts)
            s0 = seg_before[var].sel(time=ts)
            s2 = seg_after[var].sel(time=ts)
            if len(s1.time) > 0:
                s1.plot(ax=ax, color=color_at, zorder=10)
            if len(s0.time) > 0:
                s0.plot(ax=ax, color=color_before, alpha=.3, zorder=0)
            if len(s2.time) > 0:
                s2.plot(ax=ax, color=color_after, alpha=.3, zorder=0)

            ax.set_title("zoom on {}".format(name))
            ax.set_ylabel("{} [{}]".format(var, unit))

            ax.set_xlim(t - tofs, t + tofs)

        return fig
    return zoom_plot

def timeline_of(var, unit):
    def plot(seg, sonde_tracks_by_flag, seg_before, seg_after):
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
    "circling": [zoom_on("roll", "deg", tofs=np.timedelta64(3, "m")),
                 zoom_on("pitch", "deg", tofs=np.timedelta64(3, "m")),
                 zoom_on("altitude", "m", tofs=np.timedelta64(3, "m"))],
    "straight_leg": [straight_leg_detail_plot, zoom_on("roll", "deg")],
    "radar_calibration_wiggle": [zoom_on("roll", "deg")],
    "radar_calibration_tilted": [zoom_on("roll", "deg")],
    "lidar_leg": [timeline_of("altitude", "m"), zoom_on("altitude", "m")],
    "baccardi_calibration": [straight_leg_detail_plot, zoom_on("roll", "deg")],
}

def plots_for_kinds(kinds):
    return [default_segment_plot] + \
           [plot
            for kind in kinds
            for plot in SPECIAL_PLOTS.get(kind, [])]

def kinds_is_circle(kinds):
    return any(k in kinds for k in ["circle", "circling"])

class SegmentChecker:
    def __init__(self, flight):
        self.used_segment_ids = set()
        self.flight_id = flight.get("flight_id", "")

    def check_segment(self, seg, bahamas, sondes_by_flag):
        if "segment_id" in seg:
            segment_id = seg["segment_id"]
            if not segment_id.startswith(self.flight_id):
                yield "segment_id does not start with flight_id"
            if segment_id in self.used_segment_ids:
                yield "segment_id \"{}\" is duplicated".format(segment_id)
            self.used_segment_ids.add(segment_id)
        else:
            yield "segment_id is missing"

        if "kinds" in seg:
            kinds = seg["kinds"]
            if not isinstance(kinds, list):
                yield "kinds is not a list"
                del seg["kinds"]
            elif len(kinds) == 0:
                yield "segment has no kinds"
        else:
            yield "segment has no kinds attribute"
            kinds = []

        if seg["end"] <= seg["start"]:
            yield "segment ends before it starts"

        if "irregularities" in seg:
            irregularities = seg["irregularities"]
            if not isinstance(irregularities, list):
                yield "irregularities is not a list"
                del seg["irregularities"]
                irregularities = []
        else:
            yield "segment has no irregularities attribute"
            irregularities = []

        good_dropsondes = 0
        if "good_dropsondes" in seg:
            yield "good_dropsondes attribute is deprecated. uses dropsondes instead"
            good_dropsondes = seg["good_dropsondes"]

        if "dropsondes" not in seg:
            yield "dropsondes attribute is missing"
        elif not isinstance(seg["dropsondes"], dict):
            yield "dropsondes is not a mapping"
        else:
            for flag, sonde_ids in seg["dropsondes"].items():
                if not isinstance(sonde_ids, list):
                    yield "dropsondes with flag {} are not a list".format(flag)
            good_dropsondes = len(seg["dropsondes"].get("GOOD", []))

            dropsondes_from_info = {f: [s["sonde_id"] for s in sondes]
                                    for f, sondes in sondes_by_flag.items()}
            dropsondes_from_segment = {f: s
                                       for f, s in seg["dropsondes"].items()
                                       if len(s) > 0}
            if dropsondes_from_segment != dropsondes_from_info:
                yield "dropsondes in segment file are different from sondes in sondes.yaml"

        sonde_times = list(sorted([s["launch_time"]
                                   for sondes in sondes_by_flag.values()
                                   for s in sondes]))

        if good_dropsondes != len(sondes_by_flag.get("GOOD", [])):
            yield "inconsistent number of good sondes between segment file and sondes.yaml"

        t_start = np.datetime64(seg["start"])
        if kinds_is_circle(kinds) and len(sonde_times) > 0:
            seconds_to_first_sonde = (np.datetime64(sonde_times[0]) - t_start) \
                                   / np.timedelta64(1, "s")
            if abs(seconds_to_first_sonde - 60.) > .75 and len(irregularities) == 0:
                # use a little bit more that .5 sec offset to cover rounding errors
                yield "time to first sonde is not 1 minute and no irregularities are recorded"


def _main():
    basedir = os.path.abspath(os.path.dirname(__file__))
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("outfile")
    parser.add_argument("-d", "--data_path", default="../data")
    parser.add_argument("-s", "--sonde_info", help="sonde info yaml file", default=os.path.join(basedir, "sondes.yaml"))
    args = parser.parse_args()

    flightdata = yaml.load(open(args.infile), Loader=yaml.SafeLoader)
    bahamas_path = os.path.join(args.data_path,
                                "bahamas_{:%Y%m%d}_v0.4.nc".format(flightdata["date"]))
    bahamas = xr.open_dataset(bahamas_path)

    global_warnings = []
    if "flight_id" in flightdata:
        flight_id = flightdata["flight_id"]
    else:
        flight_id = ""
        global_warnings.append("flight_id is missing")

    if "platform" in flightdata:
        platform = flightdata["platform"]
    else:
        platform = "HALO"
        global_warnings.append("platform is missing, assuming 'HALO'")

    if args.sonde_info is not None:
        sonde_info = yaml.load(open(args.sonde_info), Loader=yaml.SafeLoader)
    else:
        sonde_info = []
        global_warnings.append("no sonde_info is specified, using data from unified dataset")

    sonde_info = [s for s in sonde_info if s["platform"] == platform]

    fig, ax = plt.subplots()
    ax.plot(bahamas.lon, bahamas.lat)
    im = fig2data_url(fig)
    plt.close("all")
    flightdata["plot_data"] = im

    checker = SegmentChecker(flightdata)

    for seg in flightdata["segments"]:
        t_start = np.datetime64(seg["start"])
        t_end = np.datetime64(seg["end"])
        seg_bahamas = bahamas.sel(time=slice(t_start, t_end))
        seg_before = bahamas.sel(time=slice(t_start - border_time, t_start))
        seg_after = bahamas.sel(time=slice(t_end, t_end + border_time))

        sondes_in_segment = [s
                             for s in sonde_info
                             if s["launch_time"] >= seg["start"]
                             and s["launch_time"] < seg["end"]]
        sondes_by_flag = {f: [s for s in sondes_in_segment if s["flag"] == f]
                          for f in set(s["flag"] for s in sondes_in_segment)}

        seg["sondes_by_flag"] = sondes_by_flag

        sonde_times = [s["launch_time"] for s in sondes_in_segment]

        sonde_tracks_by_flag = {
            f: bahamas.sel(time=[s["launch_time"] for s in sondes], method="nearest")
            for f, sondes in sondes_by_flag.items()
        }

        plot_data = []
        warnings = list(checker.check_segment(seg, seg_bahamas, sondes_by_flag))

        for plot in plots_for_kinds(seg.get("kinds", [])):
            try:
                plot_data.append(fig2data_url(
                    plot(seg_bahamas, sonde_tracks_by_flag, seg_before, seg_after)))
                plt.close("all")
            except Exception as e:
                warnings.append("plot could not be created: {}".format(e))

        seg["plot_data"] = plot_data
        if len(sonde_times) > 0:
            seg["time_to_first_sonde"] = (np.datetime64(sonde_times[0]) - t_start) / np.timedelta64(1, "s")
        if kinds_is_circle(seg.get("kinds", [])):
            seg["heading_difference"] = (seg_bahamas.heading.data[-1] - seg_bahamas.heading.data[0]) % 360

        seg["warnings"] = warnings

    flightdata["warnings"] = global_warnings

    tpl = env.get_template("flight.html")

    with open(args.outfile, "w") as outfile:
        outfile.write(tpl.render(flight=flightdata))

if __name__ == "__main__":
    _main()
