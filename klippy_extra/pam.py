import math

# PEP 485 isclose()
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# return true if a coordinate is within the region
# specified by min_c and max_c
def within(coord, min_c, max_c, tol=0.0):
    return (max_c[0] + tol) >= coord[0] >= (min_c[0] - tol) and \
        (max_c[1] + tol) >= coord[1] >= (min_c[1] - tol)

class PAM:
    
    def __init__(self, config):
        self.config = config
        self.x0 = self.y0 = self.x1 = self.y1 = 0
        self.points = None
        self.printer = self.config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.bed_mesh = self.printer.lookup_object('bed_mesh')
        self.offset = self.config.getfloat('offset', 0.0)
        self.z_endstop_x = self.config.getint('z_endstop_x', -1)
        self.z_endstop_y = self.config.getint('z_endstop_y', -1)
        self.optimus_prime = self.config.getboolean('optimus_prime', False)
        self.auto_reference_index = self.config.getboolean('auto_reference_index', False)
        self.toolhead_offset_left = self.config.getfloat('toolhead_offset_left', 35.0)      # EVA 3.1 Default with 8mm Probe 
        self.toolhead_offset_right = self.config.getfloat('toolhead_offset_right', 30.0)    # EVA 3.1 Default with 8mm Probe
        self.toolhead_offset_front = self.config.getfloat('toolhead_offset_front', 15.0)    # EVA 3.1 Default with 8mm Probe
        self.toolhead_offset_back = self.config.getfloat('toolhead_offset_back', 15.0)      # EVA 3.1 Default with 8mm Probe
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
        mesh_profile = param.get('PROFILE', 'default')
        if self.x0 >= self.x1 or self.y0 >= self.y1:
            self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE={0}'.format(mesh_profile))
            return
        mesh_x0 = max(self.x0, self.bed_mesh.bmc.orig_config['mesh_min'][0])
        mesh_y0 = max(self.y0, self.bed_mesh.bmc.orig_config['mesh_min'][1])
        mesh_x1 = min(self.x1, self.bed_mesh.bmc.orig_config['mesh_max'][0])
        mesh_y1 = min(self.y1, self.bed_mesh.bmc.orig_config['mesh_max'][1])
        mesh_cx = max(3, int((mesh_x1 - mesh_x0) / self.probe_x_step))
        mesh_cy = max(3, int((mesh_y1 - mesh_y0) / self.probe_y_step))
        if self.bed_mesh.bmc.orig_config['algo'] == 'lagrange' or (self.bed_mesh.bmc.orig_config['algo'] == 'bicubic' and (mesh_cx < 4 or mesh_cy < 4)):
            mesh_cx = min(6, mesh_cx)
            mesh_cy = min(6, mesh_cy)
        reference_index = self.get_reference_index(mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy)
        if self.optimus_prime == True:
            self.set_priming_location()
        self.gcode.respond_raw("PAM v0.4.0 bed mesh leveling...")
        self.gcode.respond_raw('Relative Reference Index {0}'.format(str(reference_index)))
        self.gcode.respond_raw("Mesh X0={0} Y0={1} X1={2} Y1={3}".format(str(mesh_x0), str(mesh_y0), str(mesh_x1), str(mesh_y1), ))
        self.gcode.run_script_from_command('BED_MESH_CALIBRATE PROFILE={0} mesh_min={1},{2} mesh_max={3},{4} probe_count={5},{6} relative_reference_index={7}'.format(mesh_profile, mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy, reference_index))
        self.x0 = -1
        self.y0 = -1
        self.x1 = -1
        self.y1 = -1

    def set_priming_location(self):
        ratos_gcode = self.printer.lookup_object('gcode_macro RatOS')
        prime_gcode = self.printer.lookup_object('gcode_macro PRIME')

        toolhead_min_x = max(0, self.toolhead.kin.axes_min.x)
        toolhead_min_y = max(0, self.toolhead.kin.axes_min.y)
        toolhead_max_x = self.toolhead.kin.axes_max.x
        toolhead_max_y = self.toolhead.kin.axes_max.y

        nozzle_priming = str(ratos_gcode.variables['nozzle_priming']).lower() 
        if nozzle_priming == 'primeline':
            self.toolhead_offset_left = 2
            self.toolhead_offset_right = 2
            self.toolhead_offset_front = 2
            self.toolhead_offset_back = 2

        prime_width = 15
        prime_length = 100

        prime_x = self.x0
        prime_y = self.y0

        if self.y0 - toolhead_min_y - self.toolhead_offset_front > prime_width:
            # front
            location = 'front'
            prime_y = self.y0 - self.toolhead_offset_front - (prime_width / 2)
            if self.x0 + prime_length < toolhead_max_x:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'right'
                prime_x = self.x0
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'left'
                prime_x = self.x1
        elif toolhead_max_y - self.y1 - self.toolhead_offset_back > prime_width:
            # back
            location = 'back'
            prime_y = self.y1 + self.toolhead_offset_back + (prime_width / 2)
            if self.x0 + prime_length < toolhead_max_x:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'right'
                prime_x = self.x0
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'left'
                prime_x = self.x1
        elif toolhead_max_x - self.x1 - self.toolhead_offset_right > prime_width:
            # right
            location = 'right'
            prime_x = self.x1 + self.toolhead_offset_right + (prime_width / 2)
            if self.y0 + prime_length < toolhead_max_y:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'forwards'
                prime_y = self.y0
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'backwards'
                prime_y = self.y1
        elif self.x0 - toolhead_min_x - self.toolhead_offset_left > prime_width:
            # left
            location = 'left'
            prime_x = self.x0 - self.toolhead_offset_left - (prime_width / 2)
            if self.y0 + prime_length < toolhead_max_y:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'forwards'
                prime_y = self.y0
            else:
                prime_dir = ratos_gcode.variables['nozzle_prime_direction'] = 'backwards'
                prime_y = self.y1

        self.gcode.respond_raw("Optimus Prime X={0} Y={1}".format(str(prime_x), str(prime_y)))
        self.gcode.respond_raw("Optimus Prime Location {0}".format(str(location)))
        self.gcode.respond_raw("Optimus Prime Direction {0}".format(str(prime_dir)))

        prime_gcode.variables['prime_location'] = location
        prime_gcode.variables['toolhead_offset_left'] = self.toolhead_offset_left
        prime_gcode.variables['toolhead_offset_right'] = self.toolhead_offset_right
        prime_gcode.variables['toolhead_offset_front'] = self.toolhead_offset_front
        prime_gcode.variables['toolhead_offset_back'] = self.toolhead_offset_back

        ratos_gcode.variables['nozzle_prime_start_x'] = prime_x
        ratos_gcode.variables['nozzle_prime_start_y'] = prime_y
        ratos_gcode.variables['nozzle_prime_direction'] = prime_dir

    def get_reference_index(self, mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy):
        # by default the reference index is deactivated
        reference_index = -1

        if self.auto_reference_index == False:
            return reference_index
    
        # get ratos z-endstop xy coordinates
        if self.z_endstop_x < 0 or self.z_endstop_y < 0:
            configfile = self.printer.lookup_object('configfile')
            try:
                safe_home_x = configfile.status_raw_config["gcode_macro RatOS"]["variable_safe_home_x"]
                safe_home_y = configfile.status_raw_config["gcode_macro RatOS"]["variable_safe_home_y"]
                if safe_home_x == '"middle"':
                    self.z_endstop_x = self.toolhead.kin.axes_max.x / 2.0
                else:
                    self.z_endstop_x = float(safe_home_x)
                if safe_home_y == '"middle"':
                    self.z_endstop_y = self.toolhead.kin.axes_max.y / 2.0
                else:
                    self.z_endstop_y = float(safe_home_y)
            except KeyError as e:
                self.gcode.respond_raw("PAM KeyError.")
            except ValueError as e:
                self.gcode.respond_raw("PAM ValueError.")

        # non ratos fallback, in case user hasnt specified the coordinates 
        if self.z_endstop_x < 0 or self.z_endstop_y < 0:
            self.z_endstop_x = self.toolhead.kin.axes_max.x / 2.0
            self.z_endstop_y = self.toolhead.kin.axes_max.y / 2.0

        # generate probing points, if something goes wrong it returns the default value
        if self.generate_points(mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy) == False:
            return reference_index

        # get probe xy offsets
        x_offset = y_offset = 0.
        probe = self.printer.lookup_object('probe', None)
        if probe is not None:
            x_offset, y_offset = probe.get_offsets()[:2]

        # calculate reference index
        reference_index_distance = 9999
        for i, coord in enumerate(self.points):
            distance = ((self.z_endstop_x - coord[0] - x_offset)**2 + (self.z_endstop_y - coord[1] - y_offset)**2)**0.5
            if distance < reference_index_distance:
                reference_index_distance = distance
                reference_index = i

        return reference_index
    
    def generate_points(self, mesh_x0, mesh_y0, mesh_x1, mesh_y1, mesh_cx, mesh_cy):
        x_dist = (mesh_x1 - mesh_x0) / (mesh_cx - 1)
        y_dist = (mesh_y1 - mesh_y0) / (mesh_cy - 1)
        # floor distances down to next hundredth
        x_dist = math.floor(x_dist * 100) / 100
        y_dist = math.floor(y_dist * 100) / 100
        if x_dist <= 1. or y_dist <= 1.:
            self.gcode.respond_raw("bed_mesh: min/max points too close together")
            return False

        if self.bed_mesh.bmc.radius is not None:
            # round bed, min/max needs to be recalculated
            y_dist = x_dist
            new_r = (mesh_cx // 2) * x_dist
            mesh_x0 = mesh_y0 = -new_r
            mesh_x1 = mesh_y1 = new_r
        else:
            # rectangular bed, only re-calc mesh_x1
            mesh_x1 = mesh_x0 + x_dist * (mesh_cx - 1)
        pos_y = mesh_y0
        points = []
        for i in range(mesh_cy):
            for j in range(mesh_cx):
                if not i % 2:
                    # move in positive directon
                    pos_x = mesh_x0 + j * x_dist
                else:
                    # move in negative direction
                    pos_x = mesh_x1 - j * x_dist
                if self.bed_mesh.bmc.radius is None:
                    # rectangular bed, append
                    points.append((pos_x, pos_y))
                else:
                    # round bed, check distance from origin
                    dist_from_origin = math.sqrt(pos_x*pos_x + pos_y*pos_y)
                    if dist_from_origin <= self.bed_mesh.bmc.radius:
                        points.append(
                            (self.origin[0] + pos_x, self.origin[1] + pos_y))
            pos_y += y_dist
        self.points = points
        if not self.bed_mesh.bmc.faulty_regions:
            return
        # Check to see if any points fall within faulty regions
        last_y = self.points[0][1]
        is_reversed = False
        for i, coord in enumerate(self.points):
            if not isclose(coord[1], last_y):
                is_reversed = not is_reversed
            last_y = coord[1]
            adj_coords = []
            for min_c, max_c in self.bed_mesh.bmc.faulty_regions:
                if within(coord, min_c, max_c, tol=.00001):
                    # Point lies within a faulty region
                    adj_coords = [
                        (min_c[0], coord[1]), (coord[0], min_c[1]),
                        (coord[0], max_c[1]), (max_c[0], coord[1])]
                    if is_reversed:
                        # Swap first and last points for zig-zag pattern
                        first = adj_coords[0]
                        adj_coords[0] = adj_coords[-1]
                        adj_coords[-1] = first
                    break
            if not adj_coords:
                # coord is not located within a faulty region
                continue
            valid_coords = []
            for ac in adj_coords:
                # make sure that coordinates are within the mesh boundary
                if self.bed_mesh.bmc.radius is None:
                    if within(ac, (mesh_x0, mesh_y0), (mesh_x1, mesh_y1), .000001):
                        valid_coords.append(ac)
                else:
                    dist_from_origin = math.sqrt(ac[0]*ac[0] + ac[1]*ac[1])
                    if dist_from_origin <= self.bed_mesh.bmc.radius:
                        valid_coords.append(ac)
            if not valid_coords:
                self.gcode.respond_raw("bed_mesh: Unable to generate coordinates"
                            " for faulty region at index: %d" % (i))
                return False
            self.substituted_indices[i] = valid_coords
        return True

def load_config(config):
    return PAM(config)
