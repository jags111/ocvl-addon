import cv2
import uuid
from bpy.props import EnumProperty, StringProperty

from ...extend.utils import cv_register_class, cv_unregister_class, OCVLNode, updateNode, DEVELOP_STATE_BETA, DISTANCE_TYPE_FOR_TRANSFORM_ITEMS

MASK_SIZE_ITEMS = (
    ("3", "3", "3", "", 0),
    ("5", "5", "5", "", 1),
    ("7", "7", "7", "", 2),
)


class OCVLdistanceTransformNode(OCVLNode):
    bl_develop_state = DEVELOP_STATE_BETA

    image_in = StringProperty(name="image_in", default=str(uuid.uuid4()))
    image_out = StringProperty(name="image_out", default=str(uuid.uuid4()))

    distanceType_in = EnumProperty(items=DISTANCE_TYPE_FOR_TRANSFORM_ITEMS, default='DIST_L2', update=updateNode,
        description="Type of distance. It can be CV_DIST_L1, CV_DIST_L2 , or CV_DIST_C.")
    maskSize_in = EnumProperty(items=MASK_SIZE_ITEMS, default='3', update=updateNode,
        description="Size of the distance transform mask.")

    def sv_init(self, context):
        self.inputs.new("StringsSocket", "image_in")

        self.outputs.new("StringsSocket", "image_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        kwargs = {
            'src_in': self.get_from_props("image_in"),
            'distanceType_in': self.get_from_props("distanceType_in"),
            'maskSize_in': int(self.get_from_props("maskSize_in")),
            }

        image_out = self.process_cv(fn=cv2.distanceTransform, kwargs=kwargs)
        self.refresh_output_socket("image_out", image_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, "distanceType_in")
        self.add_button(layout, "maskSize_in")


def register():
    cv_register_class(OCVLdistanceTransformNode)


def unregister():
    cv_unregister_class(OCVLdistanceTransformNode)