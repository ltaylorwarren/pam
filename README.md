# PAM - Print Area Mesh for RatOS and Klipper

- adds dynamic mesh calibration to your printer and meshes only the first layer area.
- can calculate the relative reference index for you and respects faulty regions if configured.
- supports adaptive priming for RatOS v2.x
- works with RatOS and Klipper

# Please update your PAM moonraker entry!
In case you have PAM already installed, please copy and paste the new Moonraker entry from https://github.com/HelgeKeck/pam#6-moonraker-update-manager into your moonraker.conf file.

# Update Issues
If you have problems to update to the new version, please run:
```
bash ~/pam/install.sh
```

# 1. Install
SSH into your Raspberry PI and execute:
```
cd ~/
git clone https://github.com/HelgeKeck/pam.git
bash ~/pam/install.sh
```

# 2. Activate

If you use ***RatOS***, add this line to your printer.cfg.
```ini
[include pam/ratos.cfg]
```

If you use ***Klipper***, add this line to your printer.cfg and call `PAM` instead of `BED_MESH_CALIBRATE`.

```ini
[include pam/klipper.cfg]
```

# 3. Modify your slicers start print g-code

**PrusaSlicer / SuperSlicer**
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

**SoftFever**
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single] 
```

**Ideamaker** 
```ini
MESH_CONFIG X0={print_pos_min_x} Y0={print_pos_min_y} X1={print_pos_max_x} Y1={print_pos_max_y}
START_PRINT EXTRUDER_TEMP={temperature_extruder1} BED_TEMP={temperature_heatbed}
```

**Simplify 3D V5**
```ini
MESH_CONFIG X0=[build_min_x] Y0=[build_min_y] X1=[build_max_x] Y1=[build_max_y]
START_PRINT EXTRUDER_TEMP=[extruder0_temperature] BED_TEMP=[bed0_temperature]
```

**Cura**
```ini
MESH_CONFIG X0=%MINX% Y0=%MINY% X1=%MAXX% Y1=%MAXY%
START_PRINT EXTRUDER_TEMP={material_print_temperature_layer_0} BED_TEMP={material_bed_temperature_layer_0}
```

To make PAM work with Cura you need to install a post processing plugin

1. in cura open menu ```Help -> Show configuration folder```
2. copy [MeshPrintSize.py](/cura/MeshPrintSize.py) into the ```scripts``` folder
3. restart cura
4. in cura open menu ```Extensions -> Post processing -> Modify G-Code``` and select ```Mesh Print Size```

# 4. Relative Reference Index
This is optional. PAM can calculate the relative reference index for you and respects faulty regions if configured.

More infos here: https://www.klipper3d.org/Bed_Mesh.html#the-relative-reference-index
```ini
[pam]
auto_reference_index: True      # Activate the auto reference index calculation
                                # default = False

# set this value only in case you dont home z in the middle of the build plate 
z_endstop_x: 90                 # Nozzle X-Coordinate, Klipper offsets will be respected 
                                # default = -1, RatOS uses its settings, klipper the middle of the build plate
z_endstop_y: 90                 # Nozzle Y-Coordinate, Klipper offsets will be respected
                                # default = -1, RatOS uses its settings, klipper the middle of the build plate
```

# 5. Adaptive Priming
This is optional and works only for RatOS V2.x.
```ini
[pam]
optimus_prime: True             # Activate the adaptive priming feature
                                # default = False, RatOS settings will be used

# In case you have a non EVA 3.1 Toolhead, you can configure your toolhead offsets
# These are the default values for a EVA 3.1 Toolhead  with a 8mm probe attached
toolhead_offset_left: 35
toolhead_offset_right: 30
toolhead_offset_front: 15
toolhead_offset_back: 15
```

# 6. Moonraker Update Manager
If you want to receive updates for PAM, add this at the end of the moonraker.conf file.
```ini
[update_manager pam]
type: git_repo
primary_branch: main
path: ~/pam
origin: https://github.com/HelgeKeck/pam.git
is_system_service: False
managed_services: klipper
```
