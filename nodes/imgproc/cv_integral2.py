import cv2
import uuid
from bpy.props import EnumProperty, StringProperty

from ...utils import cv_register_class, cv_unregister_class, OCVLNode, updateNode, DEVELOP_STATE_BETA


SDEPTH_ITEMS = (
    ("None", "None", "None", "", 0),
    ("CV_32S", "CV_32S", "CV_32S", "", 1),
    ("CV_32F", "CV_32F", "CV_32F", "", 2),
    ("CV_64F", "CV_64F", "CV_64F", "", 3),
)

class OCVLintegral2Node(OCVLNode):
    bl_develop_state = DEVELOP_STATE_BETA

    image_in = StringProperty(name="image_in", default=str(uuid.uuid4()))
    sum_out = StringProperty(name="sum_out", default=str(uuid.uuid4()))
    sqsum_out = StringProperty(name="sqsum_out", default=str(uuid.uuid4()))

    sdepth_in = EnumProperty(items=SDEPTH_ITEMS, default="None", update=updateNode,
        description='desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.')
    sqdepth_in = EnumProperty(items=SDEPTH_ITEMS, default="None", update=updateNode,
        description='desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.')

    def sv_init(self, context):
        self.inputs.new("StringsSocket", "image_in")

        self.outputs.new("StringsSocket", "sum_out")
        self.outputs.new("StringsSocket", "sqsum_out")

    def wrapped_process(self):
        self.check_input_requirements(["image_in"])

        sdepth_in = self.get_from_props("sdepth_in")
        sdepth_in = -1 if sdepth_in is None else sdepth_in

        sqdepth_in = self.get_from_props("sqdepth_in")
        sqdepth_in = -1 if sqdepth_in is None else sqdepth_in

        kwargs = {
            'src_in': self.get_from_props("image_in"),
            'sdepth_in': sdepth_in,
            'sqdepth_in': sqdepth_in,
            }

        sum_out, sqsum_out = self.process_cv(fn=cv2.integral2, kwargs=kwargs)
        self.refresh_output_socket("sum_out", sum_out, is_uuid_type=True)
        self.refresh_output_socket("sqsum_out", sqsum_out, is_uuid_type=True)

    def draw_buttons(self, context, layout):
        self.add_button(layout, 'sdepth_in')
        self.add_button(layout, 'sqdepth_in')


def register():
    cv_register_class(OCVLintegral2Node)


def unregister():
    cv_unregister_class(OCVLintegral2Node)
