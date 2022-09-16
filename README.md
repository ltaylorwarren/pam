# PAM for RatOS
Print Area Mesh for RatOS

Adds dynamic mesh calibration to your RatOS printer.

# Features
- Works out of the box with any printer running RatOS
- respects all settings made in RatOS
- No configuration required
- No macro changes required
- Probe agnostic
- Independent probe count for x and y direction based on the mesh configuration


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

# 3. Configure your Slicer
Modify your printer start g-code

- PrusaSlicer / SuperSlicer
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

- Ideamaker 
```ini
MESH_CONFIG X0={print_pos_min_x} Y0={print_pos_min_y} X1={print_pos_max_x} Y1={print_pos_max_y}
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

- Cura
```ini
MESH_CONFIG X0=%MINX% Y0=%MINY% X1=%MAXX% Y1=%MAXY%
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

To make PAM work with Cura you need to install a post processing plugin

1. in cura open menu ```Help->Show configuration folder```
2. copy [MeshPrintSize.py](/cura/MeshPrintSize.py) into the ```scripts``` folder
3. restart cura
4. in cura open menu ```Extensions->Post processing->Modify G-Code``` and select ```Mesh Print Size```

# 4. Update
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