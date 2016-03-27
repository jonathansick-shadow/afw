import lsst.pex.config as pexConfig
from lsst.afw.geom import xyTransformRegistry


class TransformConfig(pexConfig.Config):
    transform = xyTransformRegistry.makeField(
        doc = "an XYTransform from the registry"
    )


class TransformMapConfig(pexConfig.Config):
    transforms = pexConfig.ConfigDictField(
        doc = "Dict of coordinate system name: TransformConfig",
        keytype = str,
        itemtype = TransformConfig,
    )
    nativeSys = pexConfig.Field(
        doc = "Name of native coordinate system",
        dtype = str,
        optional = False,
    )

