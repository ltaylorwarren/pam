# PAM for RatOS
Print area mesh for RatOS

Adds dynamic mesh calibration to your RatOS printer.

# Features
- Works out of the box with any printer running RatOS
- respects all settings made in RatOS
- No configuration required
- No macro changes required
- Probe agnostic
- Independent probe count for x and y direction based on the mesh configuration


# Installation

## On your Raspberry
```
cd ~/
git clone https://github.com/HelgeKeck/pam.git
bash ~/pam/install.sh
```

## Configure Moonraker update manager (optional)
```ini
# moonraker.conf

[update_manager pam]
type: git_repo
primary_branch: main
path: ~/pam
origin: https://github.com/HelgeKeck/pam.git
is_system_service: False
```

## Define the Gcode Macro
```ini
# printer.cfg

[include pam/pam.cfg]

# optional configuration
[pam]
offset: 10          ; clearance between print area and mesh area in mm, default = 0. 
                    ; positive value = mesh area will be bigger then the print area
                    ; negative value = mesh area will be smaller then the print area
```

## Modify your printer's start g-code in your slicer
Make sure this is the first line in your Start Gcode section.

- PrusaSlicer / SuperSlicer
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
```

- Cura
```ini
MESH_CONFIG X0=%MINX% Y0=%MINY% X1=%MAXX% Y1=%MAXY%
```
