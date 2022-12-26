# PAM for RatOS
Print Area Mesh for RatOS

Adds dynamic mesh calibration to your RatOS printer.

- works out of the box with any printer running RatOS
- respects all RatOS probe and mesh settings
- adaptive purging

# 1. Install
SSH into your Raspberry PI and execute:
```
cd ~/
git clone https://github.com/HelgeKeck/pam.git
bash ~/pam/install.sh
```

# 2. Activate
Add this to the overwrite section at the end of your printer.cfg file.
```ini
# PAM
[include pam/pam.cfg]
```

# 3. Configure
Add this to the overwrite section at the end of your printer.cfg file.
```ini
# PAM
[pam]
optimus_prime: False            # enables adaptive purging
                                # default = FALSE

# toolhead offsets, to make sure the toolhead doesnt hit the prime blob
toolhead_offset_left: 35.0      # default = 35 mm
toolhead_offset_right: 30.0     # default = 30 mm
toolhead_offset_front: 15.0     # default = 15 mm
toolhead_offset_back: 15.0      # default = 15 mm
```

# 4. Modify your slicers start print g-code

- PrusaSlicer / SuperSlicer
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

- Ideamaker 
```ini
MESH_CONFIG X0={print_pos_min_x} Y0={print_pos_min_y} X1={print_pos_max_x} Y1={print_pos_max_y}
START_PRINT EXTRUDER_TEMP={temperature_extruder1} BED_TEMP={temperature_heatbed}
```

- Simplify 3D V5
```ini
MESH_CONFIG X0=[build_min_x] Y0=[build_min_y] X1=[build_max_x] Y1=[build_max_y]
START_PRINT EXTRUDER_TEMP=[extruder0_temperature] BED_TEMP=[bed0_temperature]
```

- Cura
```ini
MESH_CONFIG X0=%MINX% Y0=%MINY% X1=%MAXX% Y1=%MAXY%
START_PRINT EXTRUDER_TEMP={material_print_temperature_layer_0} BED_TEMP={material_bed_temperature_layer_0}
```

To make PAM work with Cura you need to install a post processing plugin

1. in cura open menu ```Help -> Show configuration folder```
2. copy [MeshPrintSize.py](/cura/MeshPrintSize.py) into the ```scripts``` folder
3. restart cura
4. in cura open menu ```Extensions -> Post processing -> Modify G-Code``` and select ```Mesh Print Size```

# 5. Update
If you want to receive updates for PAM put this at the end of the moonraker.conf file.
```ini
# PAM
[update_manager pam]
type: git_repo
primary_branch: main
path: ~/pam
origin: https://github.com/HelgeKeck/pam.git
is_system_service: False
```