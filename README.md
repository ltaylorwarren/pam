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


# Install
SSH into your raspberry PI and execute these commands.
```
cd ~/
git clone https://github.com/HelgeKeck/pam.git
bash ~/pam/install.sh
```

# Activate
Add this to the overwrite section at the end of your printer.cfg file.
```ini
# PAM
[include pam/pam.cfg]
```

# Configure your Slicer

Please follow these 3 steps

1. Make sure this is the first line in your Start Gcode section.
2. Make sure this is the first line in your Start Gcode section.
3. Make sure this is the first line in your Start Gcode section.

- PrusaSlicer / SuperSlicer
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
```

- Ideamaker 
```ini
MESH_CONFIG X0={print_pos_min_x} Y0={print_pos_min_y} X1={print_pos_max_x} Y1={print_pos_max_y}
```

- Cura

To make PAM work with Cura you need to install a post processing plugin

1. download Cura post processing plugin from https://github.com/HelgeKeck/pam/tree/main/cura/MeshPrintSize.py
2. in cura open menu ```Help->Show configuration folder```
3. copy the ```MeshPrintSize.py``` file into the ```scripts``` folder
4. restart cura
5. in cura open menu ```Extensions->Post processing->Modify G-Code``` and select ```Mesh Print Size```

```ini
MESH_CONFIG X0=%MINX% Y0=%MINY% X1=%MAXX% Y1=%MAXY%
```

# Update
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