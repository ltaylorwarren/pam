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
        self.optimus_prime = self.config.getboolean('optimus_prime', False)
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
        mesh_x0 = max(self.x0, self.bed_mesh.bmc.orig_config['mesh_min'][0])
        mesh_y0 = max(self.y0, self.bed_mesh.bmc.orig_config['mesh_min'][1])
        mesh_x1 = min(self.x1, self.bed_mesh.bmc.orig_config['mesh_max'][0])
        mesh_y1 = min(self.y1, self.bed_mesh.bmc.orig_config['mesh_max'][1])
        mesh_cx = max(3, int(0.5 + (mesh_x1 - mesh_x0) / self.probe_x_step))
        mesh_cy = max(3, int(0.5 + (mesh_y1 - mesh_y0) / self.probe_y_step))
        if self.bed_mesh.bmc.orig_config['algo'] == 'lagrange':
            # Lagrange interpolation tends to oscillate when using more than 6 samples
           mesh_cx = min(6, mesh_cx)
           mesh_cy = min(6, mesh_cy)
        elif self.bed_mesh.bmc.orig_config['algo'] == 'bicubic':
            # Bicubic interpolation needs at least 4 samples on each axis
            mesh_cx = max(4, mesh_cx)
            mesh_cy = max(4, mesh_cy)
        if self.optimus_prime == True:
            self.set_priming_location(mesh_x0, mesh_y0, mesh_x1, mesh_y1)
        self.gcode.respond_raw("PAM v0.1.4 bed mesh leveling...")
        self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE=pam mesh_min={0},{1} mesh_max={2},{3} probe_count={4},{5} relative_reference_index=-1'.format(mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy))

    def set_priming_location(self, mesh_x0, mesh_y0, mesh_x1, mesh_y1):
        ratos_gcode = self.printer.lookup_object('gcode_macro RatOS')

        mesh_x0 = mesh_x0
        mesh_y0 = mesh_y0
        mesh_x1 = mesh_x1
        mesh_y1 = mesh_y1

        toolhead_min_x = max(0, self.toolhead.kin.axes_min.x)
        toolhead_min_y = max(0, self.toolhead.kin.axes_min.y)
        toolhead_max_x = self.toolhead.kin.axes_max.x
        toolhead_max_y = self.toolhead.kin.axes_max.y

        prime_width = 15
        prime_length = 100

        nozzle_priming = str(ratos_gcode.variables['nozzle_priming']).lower() 
        if nozzle_priming == 'primeline':
            prime_width = 2
            self.toolhead_offset_left = 2
            self.toolhead_offset_right = 2
            self.toolhead_offset_front = 2
            self.toolhead_offset_back = 2

        prime_x = mesh_x0 + ((mesh_x1 - mesh_x0) / 2)
        prime_y = mesh_y0 + ((mesh_y1 - mesh_y0) / 2)
        if toolhead_max_x - mesh_x1 - self.toolhead_offset_right > prime_width:
            # right
            location = 'right'
            prime_x = mesh_x1 + self.toolhead_offset_right + (prime_width / 2)
            if prime_y + prime_length > toolhead_max_y:
                prime_y = toolhead_max_y - prime_length
            if prime_y < toolhead_max_y / 2:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'forwards'
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'backwards'
        elif mesh_x0 - toolhead_min_x - self.toolhead_offset_left > prime_width:
            # left
            location = 'left'
            prime_x = mesh_x0 - self.toolhead_offset_left - (prime_width / 2)
            if prime_y + prime_length > toolhead_max_y:
                prime_y = toolhead_max_y - prime_length
            if prime_y < toolhead_max_y / 2:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'forwards'
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'backwards'
        elif mesh_y0 - toolhead_min_y - self.toolhead_offset_front > prime_width:
            # front
            location = 'front'
            prime_y = mesh_y0 - self.toolhead_offset_front - (prime_width / 2)
            if prime_x + prime_length > toolhead_max_x:
                prime_x = toolhead_max_x - prime_length
            if prime_x > toolhead_max_x / 2:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'left'
                if prime_x < toolhead_max_x / 2:
                    prime_x = toolhead_min_y + prime_length + (prime_width / 2)
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'right'
                if prime_x > toolhead_max_x - prime_length - (prime_width / 2):
                    prime_x = toolhead_max_x - prime_length - (prime_width / 2)
        elif toolhead_max_y - mesh_y1 - self.toolhead_offset_back > prime_width:
            # back
            location = 'back'
            prime_y = mesh_y1 + self.toolhead_offset_back + (prime_width / 2)
            if prime_x + prime_length > toolhead_max_x:
                prime_x = toolhead_max_x - prime_length
            if prime_x > toolhead_max_x / 2:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'left'
                if prime_x < toolhead_max_x / 2:
                    prime_x = toolhead_min_y + prime_length + (prime_width / 2)
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'right'
                if prime_x > toolhead_max_x - prime_length - (prime_width / 2):
                    prime_x = toolhead_max_x - prime_length - (prime_width / 2)

        ratos_gcode.variables['nozzle_prime_start_x'] = prime_x
        ratos_gcode.variables['nozzle_prime_start_y'] = prime_y
        ratos_gcode.variables['nozzle_prime_location'] = location
        ratos_gcode.variables['nozzle_prime_direction'] = prime_dir
        ratos_gcode.variables['safe_pos_after_prime'] = self.safe_pos_after_prime

def load_config(config):
    return PAM(config)
