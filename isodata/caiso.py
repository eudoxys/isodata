"""California ISO data accessor

Collects data from CAISO historical archive sources. Valid `source` names are
as follows.

- `ems`: Historical EMS hourly load from market operations
  (see https://www.caiso.com/library/historical-ems-hourly-load) 

Example
-------

To download the CAISO EMS data from 2025, do the following

    from caiso import CAISO
    print(CAISO(2025))

which outputs the following

                                  PGE_MW     SCE_MW   SDGE_MW  VEA_MW   CAISO_MW
    2025-01-01 08:00:00+00:00   9681.776   9810.193  2193.698  82.919  21768.585
    2025-01-01 09:00:00+00:00   9429.501   9496.088  2103.146  83.159  21111.893
    2025-01-01 10:00:00+00:00   9211.415   9046.015  2017.050  84.340  20358.821
    2025-01-01 11:00:00+00:00   8976.473   8910.667  1952.761  86.946  19926.847
    2025-01-01 12:00:00+00:00   9037.663   8849.978  1937.344  91.741  19916.727
    ...                              ...        ...       ...     ...        ...
    2026-01-01 03:00:00+00:00  11763.216  10539.516  2461.768  83.379  24847.878
    2026-01-01 04:00:00+00:00  11267.992  10085.241  2362.585  81.472  23797.290
    2026-01-01 05:00:00+00:00  10899.213   9944.637  2280.701  79.450  23204.001
    2026-01-01 06:00:00+00:00  10521.685   9627.756  2209.929  76.989  22436.358
    2026-01-01 07:00:00+00:00  10096.019   9321.204  2234.588  74.800  21726.611

    [8760 rows x 5 columns]
"""

import datetime
import calendar
import warnings
import urllib

import pandas as pd

CACHE={}

class CAISO(pd.DataFrame):
    """CAISO data accessor"""

    VERSION = {
        "ems": { # data format version information
            "2019-01-01": 1,
            "2023-01-01": 2,
            "2024-01-01": 3,
            "2024-04-01": 4,
        },
    }
    """Specifies the file format versions for each data source"""

    @classmethod
    def _get_version(cls,source,year,month):
        assert source in cls.VERSION, f"{source=} is not valid"
        keys,values = list(cls.VERSION[source].keys()),list(cls.VERSION[source].values())
        keys.append(f"{datetime.datetime.now().year}-{datetime.datetime.now().month:02.0f}-01")
        values.append(values[-1])
        df = pd.DataFrame(values,pd.DatetimeIndex(keys)).resample("MS").ffill()
        key = f"{year}-{month:02.0f}-01"
        try:
            return int(df.loc[key].values[0])
        except KeyError:
            return None

    def __init__(self,
        year:int,
        month:list[int]|int|None=None,
        source:str="ems",
        ):
        """Construct CAISO dataframe

        Arguments
        ---------

        - `year`: year for which data is desired (2019 to present)

        - `month`: month or list of months for which data is desired
          (`None` gets the entire year)

        - `source`: source of data (see above)
        """

        if month is None:
            month = list(range(1,13))
        elif isinstance(month,int):
            month = [month]
        try:
            iter(month)
        except TypeError as err:
            raise TypeError(f"{month=} is not iterable") from err

        data = []
        for m in month:
            version = self._get_version(source,year,m)
            if version is None:
                break
            call = f"_{source}_v{version}"
            assert call in globals().keys(), f"{year=} is not supported/recognized for {source=}"
            df = globals()[call](year,m)
            if df is None:
                warnings.warn(f"CAISO {source} data for {m}/{year} is not available")
            else:
                data.append(df)
        if len(data) == 0:
            raise ValueError(f"no data found for CAISO {year} {source} for {month=}")
        super().__init__(pd.concat(data,axis=0))

def _ems_v1(
    year:int,
    month:int,
    precision:int=3,
    ) -> pd.DataFrame:
    """Read EMS data format version 1"""
    
    file = f"https://www.caiso.com/documents/historicalemshourlyload-{year}.xlsx"
    if not file in CACHE:
        CACHE[file] = pd.read_excel(file,
            index_col=[0,1],
            parse_dates=[0],
            usecols=range(7),
            )
    data = CACHE[file].copy().round(precision).sort_index()

    data.index = (
        data.index.get_level_values(0)
        + pd.to_timedelta(data.index.get_level_values(1) + 7, unit="h")
    ).tz_localize("UTC")
    data.columns = ["PGE_MW","SCE_MW","SDGE_MW","VEA_MW","CAISO_MW"]

    start = f"{year}-{month}-01 08:00:00+0000"
    stop = f"{year + (1 if month == 12 else 0)}-{1 if month == 12 else month+1}-01 08:00:00+0000"
    date_range = pd.date_range(start=start,end=stop,freq="1h")[:-1]

    filled = pd.DataFrame(
        {x:float('nan') for x in data.columns},
        index=pd.date_range(start=f"{year-1}-12-31 00:00:00+0000",end=f"{year+1}-01-01 23:59:59+0000",freq="1h"),
    )
    filled.loc[data.index] = data

    return filled.loc[date_range,data.columns].interpolate(method="time").dropna()


def _ems_v2(
    year:int,
    month:int,
    precision:int=3,
    ) -> pd.DataFrame:
    """Read EMS data format version 2"""
    file = f"https://www.caiso.com/documents/historicalemshourlyloadfor{year}.xlsx"
    if not file in CACHE:
        CACHE[file] = pd.read_excel(file,
            index_col=[0,1],
            parse_dates=[0],
            usecols=range(7),
            )
    data = CACHE[file].copy().round(precision).sort_index()

    data.index = (
        data.index.get_level_values(0)
        + pd.to_timedelta(data.index.get_level_values(1) + 7, unit="h")
    ).tz_localize("UTC")
    data.columns = ["PGE_MW","SCE_MW","SDGE_MW","VEA_MW","CAISO_MW"]

    if month is None:
        start = f"{year}-01-01 08:00:00+0000"
        stop = f"{year+1}-01-01 08:00:00+0000"
    else:
        start = f"{year}-{month}-01 08:00:00+0000"
        stop = f"{year + (1 if month == 12 else 0)}-{1 if month == 12 else month+1}-01 08:00:00+0000"
    date_range = pd.date_range(start=start,end=stop,freq="1h")[:-1]

    filled = pd.DataFrame(
        {x:float('nan') for x in data.columns},
        index=pd.date_range(start=f"{year-1}-12-31 00:00:00+0000",end=f"{year+1}-01-01 23:59:59+0000",freq="1h"),
    )
    filled.loc[data.index] = data

    return filled.loc[date_range,data.columns].interpolate(method="time").dropna()

def _ems_v3(
    year:int,
    month:int,
    precision:int=3,
    ) -> pd.DataFrame:
    """Read EMS data format version 3"""

    if month is None:
        data = []
        for month in range(12):
            data.append(_ems_v3(year,month+1,precision))
        return pd.concat(data,axis=0)

    monthname = calendar.month_name[month].lower()  
    file = f"https://www.caiso.com/documents/historicalemshourlyloadfor{monthname}{year}.xlsx"
    if not file in CACHE:
        CACHE[file] = pd.read_excel(file,
            index_col=[0,1],
            parse_dates=[0],
            usecols=range(7),
            )
    data = CACHE[file].copy().round(precision).sort_index()

    data.index = (
        data.index.get_level_values(0)
        + pd.to_timedelta(data.index.get_level_values(1) + 7, unit="h")
    ).tz_localize("UTC")
    data.columns = ["PGE_MW","SCE_MW","SDGE_MW","VEA_MW","CAISO_MW"]

    if month is None:
        start = f"{year}-01-01 08:00:00+0000"
        stop = f"{year+1}-01-01 08:00:00+0000"
    else:
        start = f"{year}-{month}-01 08:00:00+0000"
        stop = f"{year + (1 if month == 12 else 0)}-{1 if month == 12 else month+1}-01 08:00:00+0000"
    date_range = pd.date_range(start=start,end=stop,freq="1h")[:-1]

    filled = pd.DataFrame(
        {x:float('nan') for x in data.columns},
        index=pd.date_range(start=f"{year-1}-12-31 00:00:00+0000",end=f"{year+1}-01-01 23:59:59+0000",freq="1h"),
    )
    filled.loc[data.index] = data

    return filled.loc[date_range,data.columns].interpolate(method="time").dropna()

def _ems_v4(
    year:int,
    month:int,
    precision:int=3,
    ) -> pd.DataFrame:
    """Read EMS data format version 3"""

    if month is None:
        now  = datetime.datetime.now()
        data = []
        for month in range(12) if year < now.year else now.month:
            df = _ems_v4(year,month+1,precision)
            if df is None:
                break
            data.append(df)
        return pd.concat(data,axis=0)

    monthname = calendar.month_name[month].lower()  
    file = f"https://www.caiso.com/documents/historical-ems-hourly-load-for-{monthname}-{year}.xlsx"

    if not file in CACHE:
        try:
            CACHE[file] = pd.read_excel(file,
                index_col=[0,1],
                parse_dates=[0],
                usecols=range(7),
                )
        except urllib.error.HTTPError as err:
            return None
    data = CACHE[file].copy().round(precision).sort_index().dropna()

    data.index = (
        pd.to_datetime(data.index.get_level_values(0))
        + pd.to_timedelta(data.index.get_level_values(1) + 7, unit="h")
    ).tz_localize("UTC")
    data.columns = ["PGE_MW","SCE_MW","SDGE_MW","VEA_MW","CAISO_MW"]

    if month is None:
        start = f"{year}-01-01 08:00:00+0000"
        stop = f"{year+1}-01-01 08:00:00+0000"
    else:
        start = f"{year}-{month}-01 08:00:00+0000"
        stop = f"{year + (1 if month == 12 else 0)}-{1 if month == 12 else month+1}-01 08:00:00+0000"
    date_range = pd.date_range(start=start,end=stop,freq="1h")[:-1]

    filled = pd.DataFrame(
        {x:float('nan') for x in data.columns},
        index=pd.date_range(start=f"{year-1}-12-31 00:00:00+0000",end=f"{year+1}-01-01 23:59:59+0000",freq="1h"),
    )
    filled.loc[data.index] = data

    return filled.loc[date_range,data.columns].interpolate(method="time").dropna()


if __name__ == '__main__':

    for year in range(2019,datetime.datetime.now().year+1):
        df = CAISO(year)
        print(df,flush=True)
