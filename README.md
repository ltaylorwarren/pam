# RatOS print area bed mesh leveling
based on: https://github.com/Turge08/print_area_bed_mesh

# Installation

## On your Raspberry
```
cd ~/
git clone https://github.com/HelgeKeck/print_area_mesh.git
bash ~/print_area_mesh/install.sh
```

## Configure Moonraker update manager (optional)
```ini
# moonraker.conf

[update_manager print_area_mesh]
type: git_repo
primary_branch: main
path: ~/print_area_mesh
origin: https://github.com/HelgeKeck/print_area_mesh.git
is_system_service: False
```

## Define the Gcode Macro
```ini
# printer.cfg

[include print_area_mesh/print_area_mesh.cfg]

```

## Modify your printer's start g-code in your slicer
Make sure this is the first line in your Start Gcode section

- PrusaSlicer / SuperSlicer
```ini
MESH_CONFIG X0={first_layer_print_min[0]} Y0={first_layer_print_min[1]} X1={first_layer_print_max[0]} Y1={first_layer_print_max[1]}
```

- Cura
```ini
MESH_CONFIG X0=%MINX% Y0=%MINY% X1=%MAXX% Y1=%MAXY%
```
