import cv2
import uuid
from gettext import gettext as _
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty

from .abc_Feature2D import OCVLFeature2DNode, WORK_MODE_ITEMS, STATE_MODE_ITEMS
from ...operatores.abc import InitFeature2DOperator
from ...globals import FEATURE2D_INSTANCES_DICT
from ...utils import cv_register_class, cv_unregister_class, updateNode


HLFD_WORK_MODE_ITEMS = (
    ("DETECT", "DETECT", "DETECT", "", 0),
    ("COMPUTE", "COMPUTE", "COMPUTE", "CANCEL", 1),
    ("DETECT-COMPUTE", "DETECT-COMPUTE", "DETECT-COMPUTE", "CANCEL", 2),
)


class OCVLHarrisLaplaceFeatureDetectorNode(OCVLFeature2DNode):

    _doc = _("Class implementing the Harris-Laplace feature detector as described in [127].")
    _init_method = cv2.xfeatures2d.HarrisLaplaceFeatureDetector_create

    def update_layout(self, context):
        self.update_sockets(context)
        updateNode(self, context)

    def update_and_init(self, context):
        InitFeature2DOperator.update_class_instance_dict(self, self.id_data.name, self.name)
        self.update_sockets(context)
        updateNode(self, context)

    image_in = StringProperty(default=str(uuid.uuid4()), description=_("Input 8-bit or floating-point 32-bit, single-channel image."))
    mask_in = StringProperty(default=str(uuid.uuid4()), description=_("Optional region of interest."))
    keypoints_in = StringProperty(default=str(uuid.uuid4()), description=_(""))

    keypoints_out = StringProperty(default=str(uuid.uuid4()), description=_(""))
    descriptors_out = StringProperty(default=str(uuid.uuid4()), description=_(""))

    loc_file_load = StringProperty(default="/", description=_(""))
    loc_file_save = StringProperty(default="/", description=_(""))
    loc_work_mode = EnumProperty(items=HLFD_WORK_MODE_ITEMS, default="DETECT", update=update_layout, description=_(""))
    loc_state_mode = EnumProperty(items=STATE_MODE_ITEMS, default="INIT", update=update_layout, description=_(""))
    loc_descriptor_size = IntProperty(default=0, description=_(""))
    loc_descriptor_type = IntProperty(default=0, description=_(""))
    loc_default_norm = IntProperty(default=0, description=_(""))
    loc_class_repr = StringProperty(default="", description=_(""))

    numOctaves_init = IntProperty(default=6, min=1, max=10, update=update_and_init, description="")
    corn_thresh_init = FloatProperty(default=0.01, min=0.0001, max=0.9999, update=update_and_init, description="")
    DOG_thresh_init = FloatProperty(default=0.01, min=0.0001, max=0.9999, update=update_and_init, description="")
    maxCorners_init = IntProperty(default=5000, min=1, max=100000, update=update_and_init, description="")
    num_layers_init = IntProperty(default=4, min=1, max=10, update=update_and_init, description="")

    def sv_init(self, context):
        super().sv_init(context)

    def wrapped_process(self):
        instance = FEATURE2D_INSTANCES_DICT.get("{}.{}".format(self.id_data.name, self.name))

        if self.loc_work_mode == "DETECT":
            self._detect(instance)
        elif self.loc_work_mode == "COMPUTE":
            self._compute(instance)
        elif self.loc_work_mode == "DETECT-COMPUTE":
            self._detect_and_compute(instance)


def register():
    cv_register_class(OCVLHarrisLaplaceFeatureDetectorNode)


def unregister():
    cv_unregister_class(OCVLHarrisLaplaceFeatureDetectorNode)
