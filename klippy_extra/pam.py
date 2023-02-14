class PAM:
    
    def __init__(self, config):
        self.config = config
        self.x0 = self.y0 = self.x1 = self.y1 = 0
        self.printer = self.config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.bed_mesh = self.printer.lookup_object('bed_mesh')
        self.offset = self.config.getfloat('offset', 0.0)
        self.toolhead_offset_left = self.config.getfloat('toolhead_offset_left', 35.0)
        self.toolhead_offset_right = self.config.getfloat('toolhead_offset_right', 30.0)
        self.toolhead_offset_front = self.config.getfloat('toolhead_offset_front', 15.0)
        self.toolhead_offset_back = self.config.getfloat('toolhead_offset_back', 15.0)
        self.safe_pos_after_prime = self.config.getboolean('safe_pos_after_prime', False)
        self.gcode.register_command('PAM', self.cmd_PAM, desc=("PAM"))
        self.gcode.register_command('MESH_CONFIG', self.cmd_MESH_CONFIG, desc=("MESH_CONFIG"))
        self.printer.register_event_handler("klippy:connect", self.handle_connect)

    def handle_connect(self):
        self.toolhead = self.printer.lookup_object('toolhead')
        self.probe_x_step = float((self.bed_mesh.bmc.orig_config['mesh_max'][0] - self.bed_mesh.bmc.orig_config['mesh_min'][0]) / self.bed_mesh.bmc.orig_config['x_count'])
        self.probe_y_step = float((self.bed_mesh.bmc.orig_config['mesh_max'][1] - self.bed_mesh.bmc.orig_config['mesh_min'][1]) / self.bed_mesh.bmc.orig_config['y_count'])

    def cmd_MESH_CONFIG(self, param):
        self.x0 = param.get_float('X0', None, -1000, maxval=1000) 
        self.y0 = param.get_float('Y0', None, -1000, maxval=1000)
        self.x1 = param.get_float('X1', None, -1000, maxval=1000)
        self.y1 = param.get_float('Y1', None, -1000, maxval=1000)
        if self.x0 < 0 or self.y0 < 0:
            self.gcode.respond_raw("Wrong first layer coordinates!")

    def cmd_PAM(self, param):
        if self.x0 >= self.x1 or self.y0 >= self.y1:
            self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE=ratos')
            return
        mesh_profile = param.get('PROFILE', None, "ratos")
        mesh_x0 = max(self.x0, self.bed_mesh.bmc.orig_config['mesh_min'][0])
        mesh_y0 = max(self.y0, self.bed_mesh.bmc.orig_config['mesh_min'][1])
        mesh_x1 = min(self.x1, self.bed_mesh.bmc.orig_config['mesh_max'][0])
        mesh_y1 = min(self.y1, self.bed_mesh.bmc.orig_config['mesh_max'][1])
        mesh_cx = max(3, int((mesh_x1 - mesh_x0) / self.probe_x_step))
        mesh_cy = max(3, int((mesh_y1 - mesh_y0) / self.probe_y_step))
        if self.bed_mesh.bmc.orig_config['algo'] == 'lagrange' or (self.bed_mesh.bmc.orig_config['algo'] == 'bicubic' and (mesh_cx < 4 or mesh_cy < 4)):
            mesh_cx = min(6, mesh_cx)
            mesh_cy = min(6, mesh_cy)
        self.gcode.respond_raw("PAM v0.2.0 bed mesh leveling...")
        self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE={0} mesh_min={1},{2} mesh_max={3},{4} probe_count={5},{6} relative_reference_index=-1'.format(mesh_profile, mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy))

def load_config(config):
    return PAM(config)
