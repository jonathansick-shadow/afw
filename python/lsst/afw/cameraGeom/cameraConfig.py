import lsst.pex.config as pexConfig
from lsst.afw.geom import TransformMapConfig

__all__ = ["CameraConfig", "DetectorConfig"]


class DetectorConfig(pexConfig.Config):
    """!A configuration that represents (and can be used to construct) a Detector 
    """
    transformDict = pexConfig.ConfigField(
        "Dictionary of camera transforms keyed on the transform type.", TransformMapConfig)
    name = pexConfig.Field("Name of detector slot", str)
    id = pexConfig.Field("ID of detector slot", int)
    bbox_x0 = pexConfig.Field("x0 of pixel bounding box", int)
    bbox_y0 = pexConfig.Field("y0 of pixel bounding box", int)
    bbox_x1 = pexConfig.Field("x1 of pixel bounding box", int)
    bbox_y1 = pexConfig.Field("y1 of pixel bounding box", int)
    detectorType = pexConfig.Field("Detector type: SCIENCE=0, FOCUS=1, GUIDER=2, WAVEFRONT=3", int)
    serial = pexConfig.Field("Serial string associated with this specific detector", str)
    offset_x = pexConfig.Field(
        "x offset from the origin of the camera in mm in the transposed system.", float)
    offset_y = pexConfig.Field(
        "y offset from the origin of the camera in mm in the transposed system.", float)
    refpos_x = pexConfig.Field("x position of the reference point in the detector in pixels " +
                               "in transposed coordinates.", float)
    refpos_y = pexConfig.Field("y position of the reference point in the detector in pixels " +
                               "in transposed coordinates.", float)
    yawDeg = pexConfig.Field("yaw (rotation about z) of the detector in degrees. " +
                             "This includes any necessary rotation to go from detector coordinates to camera coordinates " +
                             "after optional transposition.", float)
    pitchDeg = pexConfig.Field("pitch (rotation about y) of the detector in degrees", float)
    rollDeg = pexConfig.Field("roll (rotation about x) of the detector in degrees", float)
    pixelSize_x = pexConfig.Field("Pixel size in the x dimension in mm", float)
    pixelSize_y = pexConfig.Field("Pixel size in the y dimension in mm", float)

    # Depending on the choice of detector coordinates, the pixel grid may need to be transposed before rotation to put
    # it in camera coordinates.
    transposeDetector = pexConfig.Field("Transpose the pixel grid before orienting in focal plane?", bool)


class CameraConfig(pexConfig.Config):
    """!A configuration that represents (and can be used to construct) a Camera
    """
    detectorList = pexConfig.ConfigDictField("List of detector configs", keytype=int, itemtype=DetectorConfig)
    transformDict = pexConfig.ConfigField(
        "Dictionary of camera transforms keyed on the transform type.", TransformMapConfig)
    name = pexConfig.Field("Name of this camera", str)

    plateScale = pexConfig.Field("Plate scale of the camera in arcsec/mm", float)
    # Note that the radial transform will also apply a scaling, so all coefficients should be
    # scaled by the plate scale in appropriate units
    radialCoeffs = pexConfig.ListField("Coefficients for radial distortion", float)
    # The following is commented until radialXYTransform supports an offset (ticket/3155)
    #boresiteOffset_x = pexConfig.Field("Offset of the camera coordinates system relative to the boresite (x value)", float)
    #boresiteOffset_y = pexConfig.Field("Offset of the camera coordinates system relative to the boresite (y value)", float)
