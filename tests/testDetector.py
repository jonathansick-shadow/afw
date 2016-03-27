#!/usr/bin/env python2
from __future__ import absolute_import, division
#
# LSST Data Management System
# Copyright 2014 LSST Corporation.
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
Tests for lsst.afw.cameraGeom.Detector
"""
import itertools
import unittest

import lsst.utils.tests
import lsst.pex.exceptions
import lsst.afw.geom as afwGeom
import lsst.afw.cameraGeom as cameraGeom
from lsst.afw.cameraGeom.testUtils import DetectorWrapper


class DetectorTestCase(unittest.TestCase):

    def testBasics(self):
        """Test getters and other basics
        """
        dw = DetectorWrapper()
        detector = dw.detector
        for methodName in ("begin", "end", "size"):
            if hasattr(detector, methodName):
                self.assertFalse(hasattr(detector, methodName))
        self.assertEquals(dw.name, detector.getName())
        self.assertEquals(dw.id, detector.getId())
        self.assertEquals(dw.type, detector.getType())
        self.assertEquals(dw.serial, detector.getSerial())
        bbox = detector.getBBox()
        for i in range(2):
            self.assertEquals(bbox.getMin()[i], dw.bbox.getMin()[i])
            self.assertEquals(bbox.getMax()[i], dw.bbox.getMax()[i])
        self.assertAlmostEquals(dw.pixelSize, detector.getPixelSize())
        self.assertEquals(len(detector), len(dw.ampInfo))

        orientation = detector.getOrientation()

        transformMap = detector.getTransformMap()
        self.assertEquals(len(transformMap), len(dw.transMap) + 1)  # add 1 for null transform
        for cameraSys in dw.transMap:
            self.assertTrue(cameraSys in transformMap)

        # make sure some complex objects stick around after detector is deleted

        detectorName = detector.getName()
        offset = dw.orientation.getFpPosition()
        del detector
        del dw
        self.assertEquals(orientation.getFpPosition(), offset)
        nativeCoordSys = transformMap.getNativeCoordSys()
        self.assertEquals(nativeCoordSys,
                          cameraGeom.CameraSys(cameraGeom.PIXELS.getSysName(), detectorName))

    def testConstructorErrors(self):
        """Test constructor errors
        """
        def duplicateAmpName(dw):
            """Set two amplifiers to the same name"""
            dw.ampInfo[1].setName(dw.ampInfo[0].getName())
        self.assertRaises(lsst.pex.exceptions.Exception, DetectorWrapper, modFunc=duplicateAmpName)

        def addBadCameraSys(dw):
            """Add an invalid camera system"""
            dw.transMap[cameraGeom.CameraSys("foo", "wrong detector")] = afwGeom.IdentityXYTransform()
        self.assertRaises(lsst.pex.exceptions.Exception, DetectorWrapper, modFunc=addBadCameraSys)

    def testTransform(self):
        """Test the transform method
        """
        dw = DetectorWrapper()
        pixOffset = dw.orientation.getReferencePoint()
        for xyMM in ((25.6, -31.07), (0, 0), (-1.234e5, 3.123e4)):
            fpPoint = afwGeom.Point2D(*xyMM)
            fpCamPoint = cameraGeom.CameraPoint(fpPoint, cameraGeom.FOCAL_PLANE)
            pixCamPoint = dw.detector.transform(fpCamPoint, cameraGeom.PIXELS)
            pixPoint = pixCamPoint.getPoint()
            for i in range(2):
                self.assertAlmostEquals(fpPoint[i]/dw.pixelSize[i] + pixOffset[i], pixPoint[i])
            fpCamPoint2 = dw.detector.transform(pixCamPoint, cameraGeom.FOCAL_PLANE)
            fpPoint2 = fpCamPoint2.getPoint()
            for i in range(2):
                self.assertAlmostEquals(fpPoint[i], fpPoint2[i])

            # test pix to pix
            pixCamPoint2 = dw.detector.transform(pixCamPoint, cameraGeom.PIXELS)
            for i in range(2):
                self.assertAlmostEquals(pixCamPoint.getPoint()[i], pixCamPoint2.getPoint()[i])

        # make sure you cannot transform to a different detector
        pixCamPoint = dw.detector.makeCameraPoint(afwGeom.Point2D(1, 1), cameraGeom.PIXELS)
        otherCamSys = cameraGeom.CameraSys(cameraGeom.PIXELS, "other detector")
        self.assertRaises(lsst.pex.exceptions.Exception, dw.detector.transform, pixCamPoint, otherCamSys)

    def testIteration(self):
        """Test iteration over amplifiers and __getitem__
        """
        dw = DetectorWrapper()
        ampList = [amp for amp in dw.detector]
        self.assertEquals(len(ampList), len(dw.ampInfo))
        for i, amp in enumerate(ampList):
            self.assertEquals(amp.getName(), dw.detector[i].getName())
            self.assertEquals(amp.getName(), dw.ampInfo[i].getName())
            self.assertEquals(amp.getName(), dw.detector[amp.getName()].getName())

    def testTransformAccess(self):
        """Test hasTransform and getTransform
        """
        detector = DetectorWrapper().detector
        for camSys in (cameraGeom.FOCAL_PLANE, cameraGeom.PIXELS, cameraGeom.TAN_PIXELS):
            # camSys may be a CameraSys or a CameraSysPrefix
            fullCamSys = detector.makeCameraSys(camSys)
            self.assertTrue(detector.hasTransform(camSys))
            self.assertTrue(detector.hasTransform(fullCamSys))
            detector.getTransform(camSys)
            detector.getTransform(fullCamSys)

        for badCamSys in (
            cameraGeom.CameraSys("badName"),
            cameraGeom.CameraSys("pixels", "badDetectorName")
        ):
            self.assertFalse(detector.hasTransform(badCamSys))
            self.assertRaises(lsst.pex.exceptions.Exception, detector.getTransform, badCamSys)

    def testMakeCameraPoint(self):
        """Test the makeCameraPoint method
        """
        dw = DetectorWrapper()
        for xyMM in ((25.6, -31.07), (0, 0)):
            point = afwGeom.Point2D(*xyMM)
            for sysName in ("csys1", "csys2"):
                for detectorName in ("", dw.name, "a different detector"):
                    cameraSys1 = cameraGeom.CameraSys(sysName, detectorName)
                    cameraPoint1 = dw.detector.makeCameraPoint(point, cameraSys1)

                    self.assertEquals(cameraPoint1.getPoint(), point)
                    self.assertEquals(cameraPoint1.getCameraSys(), cameraSys1)

                cameraSysPrefix = cameraGeom.CameraSysPrefix(sysName)
                cameraPoint2 = dw.detector.makeCameraPoint(point, cameraSysPrefix)
                predCameraSys2 = cameraGeom.CameraSys(sysName, dw.name)
                self.assertEquals(cameraPoint2.getPoint(), point)
                self.assertEquals(cameraPoint2.getCameraSys(), predCameraSys2)

    def testMakeCameraSys(self):
        """Test the makeCameraSys method
        """
        dw = DetectorWrapper()
        for sysName in ("csys1", "csys2"):
            for detectorName in ("", dw.name, "a different detector"):
                inCamSys = cameraGeom.CameraSys(sysName, detectorName)
                outCamSys = dw.detector.makeCameraSys(inCamSys)
                self.assertEquals(inCamSys, outCamSys)

            inCamSysPrefix = cameraGeom.CameraSysPrefix(sysName)
            outCamSys2 = dw.detector.makeCameraSys(inCamSysPrefix)
            self.assertEquals(outCamSys2, cameraGeom.CameraSys(sysName, dw.name))

    def testGetCorners(self):
        """Test the getCorners method
        """
        dw = DetectorWrapper()
        for cameraSys in (cameraGeom.FOCAL_PLANE, cameraGeom.PIXELS):
            cornerList = dw.detector.getCorners(cameraSys)
            for fromPoint, toPoint in itertools.izip(afwGeom.Box2D(dw.bbox).getCorners(), cornerList):
                predToCameraPoint = dw.detector.transform(
                    dw.detector.makeCameraPoint(fromPoint, cameraGeom.PIXELS),
                    cameraSys,
                )
                predToPoint = predToCameraPoint.getPoint()
                self.assertEquals(predToCameraPoint.getCameraSys().getSysName(), cameraSys.getSysName())
                for i in range(2):
                    self.assertAlmostEquals(predToPoint[i], toPoint[i])
                    if cameraSys == cameraGeom.PIXELS:
                        self.assertAlmostEquals(fromPoint[i], toPoint[i])

    def testGetCenter(self):
        """Test the getCenter method
        """
        dw = DetectorWrapper()
        ctrPixPoint = afwGeom.Box2D(dw.detector.getBBox()).getCenter()
        ctrPixCameraPoint = dw.detector.makeCameraPoint(ctrPixPoint, cameraGeom.PIXELS)
        for cameraSys in (cameraGeom.FOCAL_PLANE, cameraGeom.PIXELS):
            ctrCameraPoint = dw.detector.getCenter(cameraSys)
            self.assertEquals(ctrCameraPoint.getCameraSys().getSysName(), cameraSys.getSysName())
            ctrPoint = ctrCameraPoint.getPoint()
            predCtrCameraPoint = dw.detector.transform(ctrPixCameraPoint, cameraSys)
            predCtrPoint = predCtrCameraPoint.getPoint()
            for i in range(2):
                self.assertAlmostEquals(ctrPoint[i], predCtrPoint[i])
                if cameraSys == cameraGeom.PIXELS:
                    self.assertAlmostEquals(ctrPixPoint[i], ctrPoint[i])


def suite():
    """Returns a suite containing all the test cases in this module."""

    lsst.utils.tests.init()

    suites = []
    suites += unittest.makeSuite(DetectorTestCase)
    suites += unittest.makeSuite(lsst.utils.tests.MemoryTestCase)
    return unittest.TestSuite(suites)


def run(shouldExit = False):
    """Run the tests"""
    lsst.utils.tests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
