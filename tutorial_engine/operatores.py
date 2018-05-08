import os
import webbrowser

import bpy
import time
import logging

from bpy.props import StringProperty

from ..tutorial_engine.worker import print_keyborad_worker
from .settings import TUTORIAL_HEARTBEAT_INTERVAL, TUTORIAL_PATH
from .engine_app import NodeCommandHandler

bpy.worker_queue = []
handler = NodeCommandHandler
logger = logging.getLogger(__name__)


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    _heartbeat_counter = 0

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':
            self._heartbeat_counter += 1
            if self._heartbeat_counter % 10 == 0:
                print(time.time())
            try:
                if bpy.worker_queue:
                    request = bpy.worker_queue.pop(0)
                    kwargs = request.get("kwargs")
                    command = request.get("command")
                    for kwarg_key, kwarg_value in kwargs.items():
                        if kwarg_value[0] in ["(", "[", "{"]:
                            kwargs[kwarg_key] = eval(kwarg_value)

                    logger.info("Pop request from queue. Command: {}, kwargs: {}".format(command, kwargs))
                    if command == "StopServer":
                        return {'CANCELLED'}
                    getattr(handler, command)(**kwargs)

            except Exception as e:
                logger.exception("{}".format(e))

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(TUTORIAL_HEARTBEAT_INTERVAL, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.area.header_text_set()
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


class TutorialModeOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "node.tutorial_mode"
    bl_label = "Node Tutorial Mode"

    loc_tutorial_path = StringProperty(default="")

    def execute(self, context):
        bpy.ops.node.clean_desk()
        NodeCommandHandler.clear_node_groups()
        NodeCommandHandler.get_or_create_node_tree()
        # orange_theme()
        bpy.engine_worker_thread.start()
        # bpy.jupyter_worker_thread.start()

        # self._timer = context.window_manager.event_timer_add(1, context.window)
        # context.window_manager.modal_handler_add(self)
        if self.loc_tutorial_path:
            url = "file://" + self.loc_tutorial_path
            webbrowser.open(url)
            logger.info("Opne tutorial from URL: {}".format(url))
        return {'FINISHED'}


class TutorialModeCommandOperator(bpy.types.Operator):
    bl_idname = "node.tutorial_mode_command"
    bl_label = "Node Tutorial Mode Command"

    loc_command = StringProperty(default="")

    def execute(self, context):

        if self.loc_command == "connect_sample_and_view":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="ImageViewer", node_output="ImageSample", input_name="image_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "connect_sample_and_view_and_blur":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="ImageViewer", node_output="blur", input_name="image_in", output_name="image_out")
            NodeCommandHandler.connect_nodes(node_input="blur", node_output="ImageSample", input_name="image_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "set_ksize_on_blur":
            nt = NodeCommandHandler.get_or_create_node_tree()
            blur = nt.nodes.get('blur')
            blur.ksize_in = (10, 10)
            return {'FINISHED'}

        elif self.loc_command == "file_mode_for_image_sample":
            nt = NodeCommandHandler.get_or_create_node_tree()
            blur = nt.nodes.get('ImageSample.001')
            blur.loc_image_mode = "FILE"
            return {'FINISHED'}

        elif self.loc_command == "select_file_for_sample":
            nt = NodeCommandHandler.get_or_create_node_tree()
            blur = nt.nodes.get('ImageSample.001')
            full_tutorial_path = os.path.abspath(os.path.join(TUTORIAL_PATH, "common/ml.png"))
            blur.loc_filepath = full_tutorial_path
            return {'FINISHED'}

        elif self.loc_command == "connect_addweighted_first_input":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="addWeighted", node_output="ImageSample.001", input_name="image_1_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "connect_addweighted_second_input":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="addWeighted", node_output="blur", input_name="image_2_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command == "connect_addweighted_output":
            nt = NodeCommandHandler.get_or_create_node_tree()
            NodeCommandHandler.connect_nodes(node_input="ImageViewer", node_output="addWeighted", input_name="image_in", output_name="image_out")
            return {'FINISHED'}

        elif self.loc_command:
            keyborad_worker_thread = print_keyborad_worker(text=self.loc_command)
            keyborad_worker_thread.start()

        return {'FINISHED'}


class TutorialShowFirstStepCommandOperator(bpy.types.Operator):
    bl_idname = "node.tutorial_show_first_step"
    bl_label = "Node Tutorial Show First Step"

    loc_command = StringProperty(default="")

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'NODE_EDITOR':
                NodeCommandHandler.clear_node_groups()
                NodeCommandHandler.get_or_create_node_tree()
                NodeCommandHandler.create_node("OCVLFirstStepsNode", location=(0, 0))
                NodeCommandHandler.view_all()
                return {'FINISHED'}
        return {'CANCELLED'}




def orange_theme():
    current_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    themes_dir = os.path.abspath(os.path.join(current_dir, "../../../presets/interface_theme"))
    filepath = os.path.join(themes_dir, "blend_swap_5.xml")
    bpy.ops.script.execute_preset(
        filepath=filepath,
        menu_idname="USERPREF_MT_interface_theme_presets")


def register():
    bpy.utils.register_class(ModalTimerOperator)
    bpy.utils.register_class(TutorialModeOperator)
    bpy.utils.register_class(TutorialModeCommandOperator)
    bpy.utils.register_class(TutorialShowFirstStepCommandOperator)


def unregister():
    bpy.utils.unregister_class(TutorialShowFirstStepCommandOperator)
    bpy.utils.unregister_class(TutorialModeCommandOperator)
    bpy.utils.unregister_class(TutorialModeOperator)
    bpy.utils.unregister_class(ModalTimerOperator)
