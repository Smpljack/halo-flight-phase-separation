import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from datetime import datetime


def ds_timestamp_ind(bahamas_data, dropsonde_data, dropsonde_ind):
    """
    Return the bahamas timestamp index for a given dropsonde index.
    :param bahamas_data: unified bahamas dataset.
    :param dropsonde_data: unified dropsonde dataset.
    :param dropsonde_ind: Dropsonde index within dropsonde_data,
    e.g. the number of the dropsonde within the file, 0 indexing.
    :return:
    """
    return int(np.abs(bahamas_data['time'] -
                      dropsonde_data["launch_time"][dropsonde_ind]).argmin().values)


def max_timestamp_ind(bahamas_data, quantity, time_slice, order):
    """
    Search for local maxmimum of given order of a quantity in a bahamas
    dataset within given time slice and return its timestamp index.

    :param bahamas_data: unified bahamas dataset.
    :param quantity: bahamas_data variable name.
    :param time_slice: slice within which to search.
    :param order: How many points on each side to use to find a local minimum.
    :return: Index of timestamp.
    """
    sliced_bahamas_data = bahamas_data.sel(time=time_slice)
    sliced_ind = signal.argrelextrema(
        sliced_bahamas_data[quantity].values, np.greater, order=order)[0]
    return int(np.where(np.isin(bahamas_data['time'].values,
                                sliced_bahamas_data['time'][sliced_ind].values))[0])


def min_timestamp_ind(bahamas_data, quantity, time_slice, order):
    """
    Search for local minimum of given order of a quantity in a bahamas
    dataset within given time slice.

    :param bahamas_data: unified bahamas dataset.
    :param quantity: bahamas_data variable name.
    :param time_slice: slice within which to search.
    :param order: How many points on each side to use to find a local minimum.
    :return: Index of timestamp.
    """
    sliced_bahamas_data = bahamas_data.sel(time=time_slice)
    sliced_ind = signal.argrelextrema(
        sliced_bahamas_data[quantity].values, np.less, order=order)[0]
    return int(np.where(np.isin(bahamas_data['time'].values,
                                sliced_bahamas_data['time'][sliced_ind].values))[0])


def find_first_value_after_ts_ind(bahamas_data, quantity, timestamp_ind, apr_value, margin):
    """
    Search for the first occurence of a value (within a given margin) of any quantity
    within a bahamas dataset after a given timestamp and return the timestamp of that value.

    :param bahamas_data: unified bahamas dataset.
    :param quantity: bahamas_data variable name.
    :param timestamp_ind: timestamp index.
    :param apr_value: value to search for.
    :param margin: apr_value ± margin is the range within which values are considered to
    agree with apr_value.
    :return: timestamp index.
    """
    sliced_bahamas_data = bahamas_data.isel(time=np.arange(timestamp_ind, len(bahamas_data['time'])))
    sliced_ind = np.where(np.less(np.abs(sliced_bahamas_data[quantity] - apr_value), margin))[0][0]
    return int(np.where(np.isin(bahamas_data['time'].values,
                                sliced_bahamas_data['time'][sliced_ind].values))[0])


def find_first_value_before_ts_ind(bahamas_data, quantity, timestamp_ind, apr_value, margin):
    """
    Search for the first occurence of a value (within a given margin) of any quantity
    within a bahamas dataset before a given timestamp (closest to the given timestamp)
    and return the timestamp of that value.

    :param bahamas_data: unified bahamas dataset.
    :param quantity: bahamas_data variable name.
    :param timestamp_ind: timestamp index.
    :param apr_value: value to search for.
    :param margin: apr_value ± margin is the range within which values are considered to
    agree with apr_value.
    :return: timestamp index.
    """
    sliced_bahamas_data = bahamas_data.isel(time=np.arange(0, timestamp_ind))
    sliced_ind = np.where(np.less(np.abs(sliced_bahamas_data[quantity] - apr_value), margin))[0][-1]
    return int(np.where(np.isin(bahamas_data['time'].values,
                                sliced_bahamas_data['time'][sliced_ind].values))[0])


def plot_bahamas_timeseries(bahamas_data, ts_ind_list, label_list):
    """
    Plot some standard bahamas timeseries and scatter the timestamp indices
    contained in ts_ind_list into the plots. Used for manually assessing if
    determined timestamps are plausible.

    :param bahamas_data: unified bahamas dataset.
    :param ts_ind_list: list of timestamp indices, e.g. only contains integers.
    :param label_list: list of labels that describe the timestamps provided in ts_ind_list.
    :return: plt.figure and plt.axes objects.
    """
    plt.rcParams.update({'font.size': 20,
                         'axes.linewidth': 1.5,
                         'lines.linewidth': 2.0})
    fig, ax = plt.subplots(nrows=4, sharex=True, figsize=(15, 20))
    ax[0].plot(bahamas_data["time"], bahamas_data["roll"], color="k")
    markers_for_ts_ind(bahamas_data["time"].values, bahamas_data["roll"].values, ts_ind_list, label_list, ax[0])
    ax[0].set_ylabel('roll [°]')

    ax[1].plot(bahamas_data["time"], bahamas_data["altitude"] / 1e3, color="k")
    markers_for_ts_ind(bahamas_data["time"].values, bahamas_data["altitude"].values / 1e3,
                       ts_ind_list, label_list, ax[1])
    ax[1].set_ylabel('altitude [km]')

    ax[2].plot(bahamas_data["time"][1:], np.diff(bahamas_data["altitude"]), color="k")
    ts_ind_list_for_diff = [ts_ind - 1 if ts_ind > 0 else ts_ind for ts_ind in ts_ind_list]
    markers_for_ts_ind(bahamas_data["time"].values, np.diff(bahamas_data["altitude"].values),
                       ts_ind_list_for_diff, label_list, ax[2])
    ax[2].set_ylabel('d(altitude)/dt [m/s]')

    ax[3].plot(bahamas_data["time"], bahamas_data["heading"], color="k")
    markers_for_ts_ind(bahamas_data["time"].values, bahamas_data["heading"],
                       ts_ind_list, label_list, ax[3])
    ax[3].set_ylabel('heading [°]')
    plt.xticks(rotation=45)
    ax[3].set_xlabel('time')
    ax[3].set_xlabel('time')
    ax[0].legend(bbox_to_anchor=(1.01, 1.05))
    return fig, ax


def markers_for_ts_ind(x, y, ts_ind_list, label_list, ax):
    """
    Scatter timestamp markers into a timeseries for given time array x and associated values y.
    Timestamp indices are provided with ts_ind_list and and associated labels with label_list.

    :param x: time array.
    :param y: array of values associated with x, e.g. some bahamas quantity.
    :param ts_ind_list: list of timestamp indices, e.g. only contains integers.
    :param label_list: list of labels that describe the timestamps provided in ts_ind_list.
    :param ax: plt.axes object.
    :return: -
    """
    for enum, ts_ind in enumerate(ts_ind_list):
        ax.scatter(x[ts_ind], y[ts_ind],
                   marker="x", zorder=10, label=label_list[enum], s=100)


def dt64_to_unixtime(dt64):
    """
    Transform datetime64 object into integer with 1970-01-01 00:00:00 UTC epoch.
    :param dt64: datetime64 object.
    :return: integer containing the number of seconds since 1970-01-01 00:00:00 UTC.
    """
    return dt64.astype('datetime64[s]').astype('int')


def dt64_to_dt(dt64):
    """
    Transform datetime64 object to datetime.datetime object.
    :param dt64: numpy datetime64 object
    :return: datetime.datetime object
    """
    return datetime.utcfromtimestamp(dt64_to_unixtime(dt64))


def timestamp_ind_1min_prior(bahamas_data, timestamp_ind):
    """
    Find the timestamp index in the bahamas dataset that is 1 minute
    prior to the given timetamp_ind. Used for finding the circle start
    timestamps.
    :param bahamas_data: unified bahamas dataset.
    :param timestamp_ind: timestamp index.
    :return: timestamp index.
    """
    return int(np.argmin(np.abs(bahamas_data['time'] -
                                (bahamas_data['time'][timestamp_ind] - np.timedelta64(1, 'm')))))


def timestamp_ind_seconds_prior(bahamas_data, timestamp_ind, seconds):
    """
    Find the timestamp index in the bahamas dataset that is 'seconds'
    prior to the given timetamp_ind. Used for finding the circle start
    timestamps.
    :param bahamas_data: unified bahamas dataset.
    :param timestamp_ind: timestamp index.
    :param: seconds: Amount of seconds to go back in time.
    :return: timestamp index.
    """
    return int(np.argmin(np.abs(bahamas_data['time'] -
                                (bahamas_data['time'][timestamp_ind] -
                                 np.timedelta64(seconds, 's')))))


def exit_circle_timestamp_ind(bahamas_data, enter_circle_ts_index):
    """
    Find the timestamp index in the bahamas dataset after the given
    enter_circle_ts_index that has the closest 'heading' value as
    was present during the enter_circle_ts_index timestamp.
    This only searches within the next hour after enter_circle_ts_index.
    :param bahamas_data: unified bahamas dataset.
    :param enter_circle_ts_index: timestamp index.
    :return: timestamp index.
    """
    timestamp_1h = bahamas_data['time'][enter_circle_ts_index] + np.timedelta64(1, 'h')
    timestamp_ind_1h = int(np.argmin(np.abs(bahamas_data['time'] - timestamp_1h)))
    return np.argmin(np.abs(bahamas_data['heading'][enter_circle_ts_index + 1:timestamp_ind_1h]
                            - bahamas_data['heading'][enter_circle_ts_index])) + enter_circle_ts_index + 1

def enter_circle_timestamp_ind_given_end(bahamas_data, exit_circle_ts_index):
    """
    Find the timestamp index in the bahamas dataset prior to the given
    exit_circle_ts_index that has the closest 'heading' value as
    was present during the exit_circle_ts_index timestamp.
    This only searches within the hour prior to exit_circle_ts_index.
    :param bahamas_data: unified bahamas dataset.
    :param exit_circle_ts_index: timestamp index.
    :return: timestamp index.
    """
    timestamp_1h = bahamas_data['time'][exit_circle_ts_index] - np.timedelta64(1, 'h')
    timestamp_ind_1h = int(np.argmin(np.abs(bahamas_data['time'] - timestamp_1h)))
    return  exit_circle_ts_index - 1 - \
            np.argmin(np.abs(bahamas_data['heading'][exit_circle_ts_index-1:timestamp_ind_1h:-1]
                            - bahamas_data['heading'][exit_circle_ts_index]))
