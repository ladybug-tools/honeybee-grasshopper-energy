# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate a building (or zone) balance temperature from a ideal air load simulation
results. The balance point is the outdoor temperature at which a building switches
between heating and cooling.
_
If the outdoor temperture drops below the balance temperature, the building will
usually be in heating mode and, if the outdoor temperture is above the balance
temperature, the building will usually be in cooling mode.
_
The balance temperture concept is useful for setting things such as automated
blinds and airflow schedules since having these things directly controlled by
hourly cooling or heating demand isn't always straightforward.
_
This component works by taking the average combined heating/cooling values for
each day and the average outdoor air temperature for each day. The days with
the smallest combined heating + cooling will have their daily mean outdoor air
tempertures averaged to produce the output balance temperture.

-
    Args:
        _cooling: Data collection for the annual hourly or daily ideal air cooling
            load output from the "HB Read Room Energy Result" component.  This
            can be for a single room or the entire model.
        _heating: Data collection for the annual hourly or daily ideal air heating
            load output from the "HB Read Room Energy Result" component.  This
            can be for a single room or the entire model.
        _temperature: Data collection for the annual hourly or daily outdoor temperature.
            Most of the time, this should be the dry bulb temperature from the
            "LB Import EPW" component. However other types of temperature like
            sky temperature may improve accuracy since they include the effects
            of solar gain. Note that, whatever type of temperature is plugged
            in here determines the type of balance temperature that is output.
        _day_count_: An integer for the number of days with a low thermal energy
            load that will be averaged together to yield the balance point.
            The use of multiple days is done to help avoid anomalies introduced
            by things like variations between weekday and weekend shcedules.
            It is recommended that this be increased for models with particularly
            high variation in schedules. (Default: 10).

    Returns:
        bal_day_load: The average thermal load on the balance day. This number should
            be close to 0 if the balance temperature is accurate and this output
            is meant to give a sense of the accuracy of the balance temperature value.
        bal_temp: The outdoor balance temperature.
"""

ghenv.Component.Name = 'HB Balance Temperature'
ghenv.Component.NickName = 'BalTemp'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '6 :: Result'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import HourlyContinuousCollection, DailyCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def sum_collection(data):
    """Sum a list of data collections into a single daily collection."""
    total_data = data[0]
    for data_i in data[1:]:
        total_data = total_data + data_i
    if isinstance(total_data, HourlyContinuousCollection):
        total_data = total_data.average_daily()
    elif not isinstance(total_data, DailyCollection):
        raise TypeError('Expected Hourly or Daily data collection. '
                        'Got {}'.format(type(_temperature)))
    return total_data


if all_required_inputs(ghenv.Component):
    # set the defaut day count and ensure temperature is daily
    _day_count_ = 10 if _day_count_ is None else _day_count_
    if isinstance(_temperature, HourlyContinuousCollection):
        _temperature = _temperature.average_daily()
    elif not isinstance(_temperature, DailyCollection):
        raise TypeError('Expected Hourly or Daily data collection for '
                        '_temperature. Got {}'.format(type(_temperature)))

    # convert the heating and cooling collections to a single daily balance
    total_cool = sum_collection(_cooling)
    total_heat = sum_collection(_heating)
    total_load = total_cool + total_heat

    # check that all data collections are annual
    assert len(total_load) >= 365, 'Cooling and heating loads are not annual.'
    assert len(_temperature) >= 365, 'Temperature is not annual.'

    # sort the load to find the days with the lowest load
    temp_sort = []
    load_sort = []
    for i, (load, temp) in enumerate(sorted(zip(total_load, _temperature))):
        if i == _day_count_:
            break
        temp_sort.append(temp)
        load_sort.append(load)

    # return the average temperature and balance day load
    print len(temp_sort)
    bal_day_load = sum(load_sort) / _day_count_
    bal_temp = sum(temp_sort) / _day_count_
