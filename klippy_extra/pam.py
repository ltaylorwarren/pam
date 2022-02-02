import time
from math import fabs
from re import T

class PAM:

    # -----------------------------------------------------------------------------------------------------------------------------
    # Initialize
    # -----------------------------------------------------------------------------------------------------------------------------
    def __init__(self, config):
        self.config = config
        self.printer = self.config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        self.bed_mesh = self.printer.lookup_object('bed_mesh')

        self.load_settings()
        self.register_commands()
        self.register_handle_connect()

    def register_handle_connect(self):
        self.printer.register_event_handler("klippy:connect", self.execute_handle_connect)

    def execute_handle_connect(self):
        self.toolhead = self.printer.lookup_object('toolhead')

        self.x0 = self.toolhead.kin.axes_min.x
        self.y0 = self.toolhead.kin.axes_min.y
        self.x1 = self.toolhead.kin.axes_max.x
        self.y1 = self.toolhead.kin.axes_max.y

        self.probe_x_step = float((self.bed_mesh.bmc.orig_config['mesh_max'][0] - self.bed_mesh.bmc.orig_config['mesh_min'][0]) / self.bed_mesh.bmc.orig_config['x_count'])
        self.probe_y_step = float((self.bed_mesh.bmc.orig_config['mesh_max'][1] - self.bed_mesh.bmc.orig_config['mesh_min'][1]) / self.bed_mesh.bmc.orig_config['y_count'])

    # -----------------------------------------------------------------------------------------------------------------------------
    # Settings
    # -----------------------------------------------------------------------------------------------------------------------------
    def load_settings(self):
        self.offset = self.config.getfloat('offset', 0.)

    # -----------------------------------------------------------------------------------------------------------------------------
    # GCode Registration
    # -----------------------------------------------------------------------------------------------------------------------------
    def register_commands(self):
        self.gcode.register_command('PAM', self.cmd_PAM, desc=("PAM"))
        self.gcode.register_command('MESH_CONFIG', self.cmd_MESH_CONFIG, desc=("MESH_CONFIG"))

    def cmd_MESH_CONFIG(self, param):
        self.x0 = param.get_float('X0', None, minval=self.toolhead.kin.axes_min.x, maxval=self.toolhead.kin.axes_max.x) 
        self.y0 = param.get_float('Y0', None, minval=self.toolhead.kin.axes_min.y, maxval=self.toolhead.kin.axes_max.y)
        self.x1 = param.get_float('X1', None, minval=self.toolhead.kin.axes_min.x, maxval=self.toolhead.kin.axes_max.x)
        self.y1 = param.get_float('Y1', None, minval=self.toolhead.kin.axes_min.y, maxval=self.toolhead.kin.axes_max.y)

    def cmd_PAM(self, param):
        if self.x0 >= self.x1 or self.y0 >= self.y1:
            self.gcode.respond_raw("Wrong first layer coordinates, using default mesh area!")
            self.mesh()
            return

        mesh_x0 = max(self.x0 - self.offset, self.bed_mesh.bmc.orig_config['mesh_min'][0])
        mesh_y0 = max(self.y0 - self.offset, self.bed_mesh.bmc.orig_config['mesh_min'][1])
        mesh_x1 = min(self.x1 + self.offset, self.bed_mesh.bmc.orig_config['mesh_max'][0])
        mesh_y1 = min(self.y1 + self.offset, self.bed_mesh.bmc.orig_config['mesh_max'][1])
        mesh_cx = max(3, int((mesh_x1 - mesh_x0) / self.probe_x_step))
        mesh_cy = max(3, int((mesh_y1 - mesh_y0) / self.probe_y_step))

        self.area_mesh([mesh_x0, mesh_y0], [mesh_x1, mesh_y1], [mesh_cx, mesh_cy])

    # -----------------------------------------------------------------------------------------------------------------------------
    # Mesh
    # -----------------------------------------------------------------------------------------------------------------------------
    def mesh(self):
        self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE=ratos')

    def area_mesh(self, mesh_min, mesh_max, probe_count):
        self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE=ratos mesh_min={0},{1} mesh_max={2},{3} probe_count={4},{5}'.format(mesh_min[0], mesh_min[1], mesh_max[0], mesh_max[1], probe_count[0], probe_count[1]))

def load_config(config):
    return PAM(config)
