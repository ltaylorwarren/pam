# PAM for RatOS
Print area mesh for RatOS

Adds dynamic mesh calibration to your RatOS printer.

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
