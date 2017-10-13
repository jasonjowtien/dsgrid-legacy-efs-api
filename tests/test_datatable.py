import numpy as np
import pandas as pd
from dsgrid.datatable import Datatable
from .temphdf5 import TempHDF5Filepath
from dsgrid.datafile import Datafile
from dsgrid.enumeration import (
    sectors_subsectors, states, enduses, hourly2012
)

def make_data(enduses, times):
    return pd.DataFrame({
        enduse: np.random.rand(len(times))
        for enduse in enduses
        }, index=times)


def test_datatable_read():

    eus1 = ["heating", "cooling"]
    data1 = make_data(eus1, hourly2012.ids)
    data2 = make_data(eus1, hourly2012.ids)

    eus2 = ["heating", "cooling", "fans", "pumps"]
    data3 = make_data(eus2, hourly2012.ids)
    data4 = make_data(eus2, hourly2012.ids)

    with TempHDF5Filepath() as filepath:

        datafile = Datafile(filepath, sectors_subsectors, states, enduses, hourly2012)

        sector = datafile.add_sector("com__Laboratory", eus1)
        sector.add_data(data1, ["CO", "TN", "CA"], [1.0, 2.3, 6.7])
        sector["IL"] = data2

        sector = datafile.add_sector("ind__11", eus2)
        sector.add_data(data3, ["KS", "MO"], [1.3, 8.6])
        sector["WA"] = data4

        dt = Datatable(datafile)

        assert(len(dt.data) == 8784*(2*4 + 4*3))
