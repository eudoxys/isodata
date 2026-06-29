"""Electricity market data accessor

The `isodata` package provides data accessor for the follow US isodata
markets.

- `isodata.caiso.CAISO`: California ISO

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
