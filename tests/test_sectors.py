import numpy as np
import pandas as pd
from .temphdf5 import TempHDF5

from dsgrid.dataformat import Sector, Subsector, read_sectors, write_sectors, standard_counties, write_counties, EndUse, write_enduses
import dsgrid.timeformats as timeformats

# TODO: Probably potential for more tests here

othercounties = [(county.state_fips,county.county_fips) for county in standard_counties[3:]]

def test_sectors():

    # Add and populate a sector

    tfmt = timeformats.hourofweekdayweekend
    timestamps = tfmt.timeindex()
    enduses = ['Space Heating',
               'Space Cooling',
               'Water Heating',
               'Other']

    df1 = pd.DataFrame(10 + np.random.randn(48, 4),
                        columns=enduses,
                        index=timestamps)
    df2 = pd.DataFrame(10 + np.random.randn(48, 4),
                        columns=enduses,
                        index=timestamps)

    residential = Sector("residential", "Residential")
    residential.add_subsector("sfd", "Single Family Detached", tfmt, enduses)
    assert residential.sfd == Subsector("sfd", "Single Family Detached", tfmt, enduses)

    residential.sfd[(1,1)] = df1
    residential.sfd[[(1,3), (1,5)] + othercounties] = df2

    assert (residential.sfd[(1,1)].columns == enduses).all()
    assert (residential.sfd[(1,1)].index == tfmt.timeindex()).all()
    assert not residential.sfd[(1,1)].equals(residential.sfd[(1,5)])
    assert residential.sfd[(1,3)].equals(residential.sfd[(1,5)])

    # Add another sector

    enduses = ['Space Heating',
               'Space Cooling',
               'Water Heating',
               'Refrigeration',
               'Other']
    df3 = df1 + 10
    df3["Refrigeration"] = 20 + np.random.randn(48)
    df3["Random Extra Column"] = 20 + np.random.randn(48)
    df4 = df2 + 10
    df4["Refrigeration"] = 20 + np.random.randn(48)

    commercial = Sector("commercial", "Commercial")
    commercial.add_subsector("retail", "Retail", tfmt, enduses)
    assert commercial.retail == Subsector("retail", "Retail", tfmt, enduses)

    commercial.retail[[(1,1), (1,5)]] = df3
    commercial.retail[[(1,3)] + othercounties] = df4

    assert not commercial.retail[(1,1)].equals(commercial.retail[(1,3)])
    assert commercial.retail[(1,3)].equals(commercial.retail[(8,59)])


    tfmt = timeformats.hourofyear
    timestamps = tfmt.timeindex()
    df5 = pd.DataFrame(10 + np.random.randn(8784, 5),
                        columns=enduses,
                        index=timestamps)
    df6 = pd.DataFrame(10 + np.random.randn(8784, 5),
                        columns=enduses,
                        index=timestamps)

    commercial.add_subsector("office", "Office", tfmt, enduses)
    assert commercial.office == Subsector("office", "Office", tfmt, enduses)

    commercial.office[(1,5)] = df5
    commercial.office[[(1,1), (1,3)] + othercounties] = df6

    assert commercial.office[(1,1)].equals(commercial.office[(1,3)])
    assert not commercial.office[(1,1)].equals(commercial.office[(1,5)])

    # Write sectors out and read back in

    sectors = {}
    for sector in [residential, commercial]:
        sectors[sector.slug] = sector

    with TempHDF5() as testfile:

        write_counties(testfile, standard_counties)
        write_enduses(testfile, [EndUse(eu) for eu in enduses])
        write_sectors(testfile, sectors, county_check=False)

        h5sectors = read_sectors(testfile)

        assert(h5sectors == sectors)
