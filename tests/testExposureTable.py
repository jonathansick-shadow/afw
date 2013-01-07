#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
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
Tests for lsst.afw.table.ExposureTable

Run with:
   ./testExposureTable.py
or
   python
   >>> import testExposureTable; testExposureTable.run()
"""

import sys
import os
import unittest
import numpy

import lsst.utils.tests
import lsst.pex.exceptions
import lsst.afw.table
import lsst.afw.geom
import lsst.afw.coord
import lsst.afw.image
import lsst.afw.detection

try:
    type(display)
except NameError:
    display = False

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class ExposureTableTestCase(unittest.TestCase):

    @staticmethod
    def createWcs():
        metadata = lsst.daf.base.PropertySet()
        metadata.set("SIMPLE",                    "T")
        metadata.set("BITPIX",                  -32)
        metadata.set("NAXIS",                    2)
        metadata.set("NAXIS1",                 1024)
        metadata.set("NAXIS2",                 1153)
        metadata.set("RADECSYS", 'FK5')
        metadata.set("EQUINOX",                2000.)
        metadata.setDouble("CRVAL1",     215.604025685476)
        metadata.setDouble("CRVAL2",     53.1595451514076)
        metadata.setDouble("CRPIX1",     1109.99981456774)
        metadata.setDouble("CRPIX2",     560.018167811613)
        metadata.set("CTYPE1", 'RA---SIN')
        metadata.set("CTYPE2", 'DEC--SIN')
        metadata.setDouble("CD1_1", 5.10808596133527E-05)
        metadata.setDouble("CD1_2", 1.85579539217196E-07)
        metadata.setDouble("CD2_2", -5.10281493481982E-05)
        metadata.setDouble("CD2_1", -8.27440751733828E-07)
        return lsst.afw.image.makeWcs(metadata)

    def comparePsfs(self, psf1, psf2):
        psf1 = lsst.afw.detection.DoubleGaussianPsf.swigConvert(psf1)
        psf2 = lsst.afw.detection.DoubleGaussianPsf.swigConvert(psf2)
        self.assert_(psf1 is not None)
        self.assert_(psf2 is not None)
        self.assertEqual(psf1.getKernel().getWidth(), psf2.getKernel().getWidth())
        self.assertEqual(psf1.getKernel().getHeight(), psf2.getKernel().getHeight())
        self.assertEqual(psf1.getSigma1(), psf2.getSigma1())
        self.assertEqual(psf1.getSigma2(), psf2.getSigma2())
        self.assertEqual(psf1.getB(), psf2.getB())

    def setUp(self):
        schema = lsst.afw.table.ExposureTable.makeMinimalSchema()
        self.ka = schema.addField("a", type=float, doc="doc for a")
        self.kb = schema.addField("b", type=int, doc="doc for b")
        self.cat = lsst.afw.table.ExposureCatalog(schema)
        self.wcs = self.createWcs()
        self.psf = lsst.afw.detection.DoubleGaussianPsf(17, 17, 3, 6, 0.1)
        self.bbox0 = lsst.afw.geom.Box2I(
            lsst.afw.geom.Box2D(
                self.wcs.getPixelOrigin() - lsst.afw.geom.Extent2D( 5.0,  4.0),
                self.wcs.getPixelOrigin() + lsst.afw.geom.Extent2D(20.0, 30.0)
                )
            )
        self.bbox1 = lsst.afw.geom.Box2I(
            lsst.afw.geom.Box2D(
                self.wcs.getPixelOrigin() - lsst.afw.geom.Extent2D(15.0, 40.0),
                self.wcs.getPixelOrigin() + lsst.afw.geom.Extent2D( 3.0,  6.0)
                )
            )
        record0 = self.cat.addNew()
        record0.setId(1)
        record0.set(self.ka, numpy.pi)
        record0.set(self.kb, 4)
        record0.setBBox(self.bbox0)
        record0.setPsf(self.psf)
        record0.setWcs(self.wcs)
        record1 = self.cat.addNew()
        record1.setId(2)
        record1.set(self.ka, 2.5)
        record1.set(self.kb, 2)
        record1.setWcs(self.wcs)
        record1.setBBox(self.bbox1)

    def tearDown(self):
        del self.cat
        del self.psf
        del self.wcs

    def testAccessors(self):
        record0 = self.cat[0]
        record1 = self.cat[1]
        self.assertEqual(record0.getId(), 1)
        self.assertEqual(record1.getId(), 2)
        self.assertEqual(record0.getWcs(), self.wcs)
        self.assertEqual(record1.getWcs(), self.wcs)
        self.assertEqual(record0.getBBox(), self.bbox0)
        self.assertEqual(record1.getBBox(), self.bbox1)
        self.comparePsfs(record0.getPsf(), self.psf)
        self.assertEqual(record1.getPsf(), None)

    def testPersistence(self):
        filename1 = "ExposureTable1.fits"
        self.cat.writeFits(filename1)
        cat1 = lsst.afw.table.ExposureCatalog.readFits(filename1)
        os.remove(filename1)
        self.assertEqual(self.cat[0].get(self.ka), cat1[0].get(self.ka))
        self.assertEqual(self.cat[0].get(self.kb), cat1[0].get(self.kb))
        self.comparePsfs(self.cat[0].getPsf(), cat1[0].getPsf())
        self.assertEqual(self.cat[0].getWcs(), cat1[0].getWcs())
        self.assertEqual(self.cat[1].get(self.ka), cat1[1].get(self.ka))
        self.assertEqual(self.cat[1].get(self.kb), cat1[1].get(self.kb))
        self.assertEqual(self.cat[1].getWcs(), cat1[1].getWcs())
        self.assertTrue(self.cat[1].getPsf() is None)
        self.assertEqual(self.cat[0].getWcs().getId(), self.cat[1].getWcs().getId()) # compare citizen IDs

    def testGeometry(self):
        bigBox = lsst.afw.geom.Box2D(lsst.afw.geom.Box2I(self.bbox0))
        bigBox.include(lsst.afw.geom.Box2D(self.bbox1))
        points = (numpy.random.rand(100, 2) * numpy.array([bigBox.getWidth(), bigBox.getHeight()])
                  + numpy.array([bigBox.getMinX(), bigBox.getMinY()]))

        # make a very slightly perturbed wcs so the celestial transform isn't a no-op
        crval2 = self.wcs.getSkyOrigin()
        crval2.reset(crval2.getLongitude() + 5 * lsst.afw.geom.arcseconds,
                     crval2.getLatitude() - 5 * lsst.afw.geom.arcseconds)
        wcs2 = lsst.afw.image.Wcs(
            crval2.getPosition(), self.wcs.getPixelOrigin() + lsst.afw.geom.Extent2D(30.0, -50.0),
            self.wcs.getCDMatrix() * 1.1
            )
        for x1, y1 in points:
            p1 = lsst.afw.geom.Point2D(x1, y1)
            c = self.wcs.pixelToSky(x1, y1)
            p2 = wcs2.skyToPixel(c)
            subset1 = self.cat.findContains(c)
            subset2 = self.cat.findContains(p2, wcs2)
            for record in self.cat:
                inside = lsst.afw.geom.Box2D(record.getBBox()).contains(p1)
                self.assertEqual(inside, record.contains(c))
                self.assertEqual(inside, record.contains(p2, wcs2))
                self.assertEqual(inside, record.contains(p1, self.wcs))
                self.assertEqual(inside, record in subset1)
                self.assertEqual(inside, record in subset2)
            

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def suite():
    """Returns a suite containing all the test cases in this module."""

    lsst.utils.tests.init()

    suites = []
    suites += unittest.makeSuite(ExposureTableTestCase)
    suites += unittest.makeSuite(lsst.utils.tests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(shouldExit = False):
    """Run the tests"""
    lsst.utils.tests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
