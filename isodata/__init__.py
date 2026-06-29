"""Electricity market data accessor

The `isodata` package provides data accessor for the follow US isodata
markets.

- `isodata.caiso.CAISO`: California ISO

Current datasets available are

| ISO | Dataset | Fields
| --- | ------- | ------
| [CAISO](isodata/caiso.html) | `ems` | `PGE_MW`, `SCE_MW`, `SDGE_MW`, `VEA_MW`, `CAISO_MW`

Installation
------------

The following shell script installs the `isodata` package in Python

    python3 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade pip
    pip install git+https://github.com/eudoxys/isodata

The following python3 commands download the 2021 EMS data from CAISO

    from isodata import CAISO
    CAISO(2021)

which outputs

                                  PGE_MW     SCE_MW   SDGE_MW  VEA_MW   CAISO_MW
    2021-01-01 08:00:00+00:00   9644.626   9684.683  2042.954  74.968  21447.230
    2021-01-01 09:00:00+00:00   9252.453   9315.383  1939.956  75.012  20582.803
    2021-01-01 10:00:00+00:00   8977.655   9013.844  1862.010  76.598  19930.107
    2021-01-01 11:00:00+00:00   8829.848   8883.723  1829.314  78.424  19621.309
    2021-01-01 12:00:00+00:00   8845.555   8851.990  1831.502  81.843  19610.889
    ...                              ...        ...       ...     ...        ...
    2022-01-01 03:00:00+00:00  12160.480  11698.090  2565.490  88.360  26512.410
    2022-01-01 04:00:00+00:00  11823.130  11382.810  2470.360  87.210  25763.510
    2022-01-01 05:00:00+00:00  11468.940  11088.230  2373.370  89.850  25020.390
    2022-01-01 06:00:00+00:00  11029.680  10697.690  2257.010  91.260  24075.630
    2022-01-01 07:00:00+00:00  10584.540  10438.070  2127.610  92.580  23242.810

    [8760 rows x 5 columns]

Citation
--------

To cite this dataset or package use the following:

- Chassin, David P., "ISO Data" (2026). URL: https://www.eudoxys.com/isodata.

Package Information
-------------------

- Documentation: https://www.eudoxys.com/isodata

- Source code: https://github.com/eudoxys/isodata

- Issues: https://github.com/eudoxys/isodata/issues

- License: https://github.com/eudoxys/isodata/blob/main/LICENSE

- Dependencies:

  - [openpyxl](https://pypi.org/project/openpyxl)
  - [pandas](https://pypi.org/project/pandas)
  - [pip-system-certs](https://pypi.org/project/pip-system-certs)
"""

from .caiso import CAISO
