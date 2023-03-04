# Prevent running as root.
if [ ${UID} == 0 ]; then
    echo -e "DO NOT RUN THIS SCRIPT AS 'root' !"
    echo -e "If 'root' privileges needed, you will prompted for sudo password."
    exit 1
fi

# Force script to exit if an error occurs
set -e

# Find SRCDIR from the pathname of this script
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"

# Default Parameters
MACRO_DIR=""
KLIPPY_EXTRAS_DIR="${HOME}/klipper/klippy/extras"
KLIPPER_CONFIG_DIR="${HOME}/klipper_config"
PRINTER_DATA_CONFIG_DIR="${HOME}/printer_data/config"

function get_ratos_version {
    if [ -d "${KLIPPER_CONFIG_DIR}" ]; then
        echo -e "installing into klipper config dir..."
        MACRO_FILE="ratos_v1.cfg"
        CONFIG_DIR="${KLIPPER_CONFIG_DIR}"
    else
        if [ -d "${PRINTER_DATA_CONFIG_DIR}" ]; then
            echo -e "installing into printer data config dir..."
            MACRO_FILE="ratos_v2.cfg"
            CONFIG_DIR="${PRINTER_DATA_CONFIG_DIR}"
        else
            echo -e "ERROR: No RatOS config folder found."
            exit 1
        fi
    fi
    MACRO_DIR="${CONFIG_DIR}/pam"
}

function start_klipper {
    sudo systemctl restart klipper
}

function stop_klipper {
    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F "klipper.service")" ]; then
        sudo systemctl stop klipper
    else
        echo "Klipper service not found, please install Klipper first"
        exit 1
    fi
}

function create_macro_dir {
    if [ -d "${MACRO_DIR}" ]; then
        rm -rf "${MACRO_DIR}" 
    fi
    mkdir "${MACRO_DIR}"
}

function link_macro {
    if [ -d "${MACRO_DIR}" ]; then
        rm -f "${MACRO_DIR}/ratos.cfg"
        ln -sf "${SRCDIR}/klipper_macro/${MACRO_FILE}" "${MACRO_DIR}/ratos.cfg"
        rm -f "${MACRO_DIR}/pam.cfg"
        ln -sf "${SRCDIR}/klipper_macro/pam.cfg" "${MACRO_DIR}/pam.cfg"
        rm -f "${MACRO_DIR}/klipper.cfg"
        ln -sf "${SRCDIR}/klipper_macro/klipper.cfg" "${MACRO_DIR}/klipper.cfg"
    else
        echo -e "ERROR: ${MACRO_DIR} not found."
        exit 1
    fi
}

function link_extra {
    if [ -d "${KLIPPY_EXTRAS_DIR}" ]; then
        rm -f "${KLIPPY_EXTRAS_DIR}/pam.py"
        ln -sf "${SRCDIR}/klippy_extra/pam.py" "${KLIPPY_EXTRAS_DIR}/pam.py"
    else
        echo -e "ERROR: ${KLIPPY_EXTRAS_DIR} not found."
        exit 1
    fi
}

echo -e ""
echo -e "    ___  ___  __  __ "
echo -e "   | _ \/   \|  \/  |"
echo -e "   |  _/| - || |\/| |"
echo -e "   |_|  |_|_||_|  |_|"
echo -e ""
echo -e "Print Area Mesh for Klipper"
echo -e ""
get_ratos_version
stop_klipper
create_macro_dir
link_macro
link_extra
start_klipper
echo -e ""
echo -e "Installation finished!"
echo -e ""
exit 0
