#!/usr/bin/env python
#
# LSST Data Management System
# Copyright 2008-2014 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

"""
Tests for ValidPolygon

Run with:
   ./testValidPolygon.py
or
   python
   >>> import testValidPolygonTestCase; testPolygonTestCase.run()
"""

import os
import unittest
import lsst.utils.tests as utilsTests
import lsst.afw.geom as afwGeom
import lsst.afw.image as afwImage
import lsst.afw.table as afwTable


from lsst.afw.geom.polygon import Polygon

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


class ValidPolygonTestCase(utilsTests.TestCase):

    def setUp(self):
        self.bbox = afwGeom.Box2I(afwGeom.Point2I(0, 0), afwGeom.Point2I(20, 20))
        x = [0, 0, 10, 10]
        y = [0, 10, 10, 0]
        self.polygon = Polygon([afwGeom.Point2D(xc, yc) for xc, yc in zip(x, y)])

    def testPersistence(self):
        """Test that we can round-trip an ValidPolygon through FITS persistence."""
        filename = "testValidPolygon.fits"
        self.polygon.writeFits(filename)
        polygon2 = Polygon.readFits(filename)
        self.assertEqual(self.polygon, polygon2)
        os.remove(filename)

    def testExposurePersistence(self):
        """Test that the ValidPolygon is saved with an Exposure"""
        filename = "testValidPolygon.fits"
        exposure1 = afwImage.ExposureF(self.bbox)
        exposure1.getInfo().setValidPolygon(self.polygon)
        exposure1.writeFits(filename)
        exposure2 = afwImage.ExposureF(filename)
        polygon2 = exposure2.getInfo().getValidPolygon()
        self.assertEqual(self.polygon, polygon2)
        os.remove(filename)

    def testExposureRecordPersistence(self):
        """Test that the ValidPolygon is saved with an ExposureRecord"""
        filename = "testValidPolygon.fits"
        cat1 = afwTable.ExposureCatalog(afwTable.ExposureTable.makeMinimalSchema())
        record1 = cat1.addNew()
        record1.setValidPolygon(self.polygon)
        cat1.writeFits(filename)
        cat2 = afwTable.ExposureCatalog.readFits(filename)
        record2 = cat2[0]
        polygon2 = record2.getValidPolygon()
        self.assertEqual(self.polygon, polygon2)
        os.remove(filename)

    def testExposureCatalogBackwardsCompatibility(self):
        """Test that we can read an ExposureCatalog written with an old version of the code."""
        filename = os.path.join(os.environ["AFW_DIR"], "tests", "data", "version-0-ExposureCatalog.fits")
        cat = afwTable.ExposureCatalog.readFits(filename)
        record = cat[0]
        self.assertIsNone(record.getValidPolygon())

        filename2 = os.path.join(os.environ["AFW_DIR"], "tests", "data", "version-1-ExposureCatalog.fits")
        cat2 = afwTable.ExposureCatalog.readFits(filename2)
        record2 = cat2[0]
        self.assertIsNone(record2.getValidPolygon())

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(ValidPolygonTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)


def run(shouldExit = False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
