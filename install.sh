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
KLIPPER_CONFIG_DIR="${HOME}/klipper_config"
KLIPPY_EXTRAS="${HOME}/klipper/klippy/extras"
MACRO_DIR="${HOME}/klipper_config/pam"

function stop_klipper {
    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F "klipper.service")" ]; then
        sudo systemctl stop klipper
    else
        echo "Klipper service not found, please install Klipper first"
        exit 1
    fi
}

function start_klipper {
    sudo systemctl restart klipper
}

function create_macro_dir {
    if [ -d "${MACRO_DIR}" ]; then
        rm -rf "${MACRO_DIR}" 
    fi
    if [ -d "${KLIPPER_CONFIG_DIR}" ]; then
        mkdir "${MACRO_DIR}"
    else
        echo -e "ERROR: ${KLIPPER_CONFIG_DIR} not found."
        exit 1
    fi
}

function link_macro {
    if [ -d "${KLIPPER_CONFIG_DIR}" ]; then
        if [ -d "${MACRO_DIR}" ]; then
            rm -f "${MACRO_DIR}/pam.cfg"
            ln -sf "${SRCDIR}/klipper_macro/pam.cfg" "${MACRO_DIR}/pam.cfg"
        else
            echo -e "ERROR: ${MACRO_DIR} not found."
            exit 1
        fi
    else
        echo -e "ERROR: ${KLIPPER_CONFIG_DIR} not found."
        exit 1
    fi
}

function link_extra {
    if [ -d "${KLIPPY_EXTRAS}" ]; then
        rm -f "${KLIPPY_EXTRAS}/pam.py"
        ln -sf "${SRCDIR}/klippy_extra/pam.py" "${KLIPPY_EXTRAS}/pam.py"
    else
        echo -e "ERROR: ${KLIPPY_EXTRAS} not found."
        exit 1
    fi
}

### MAIN

# Parse command line arguments
while getopts "c:h" arg; do
    if [ -n "${arg}" ]; then
        case $arg in
            c)
                KLIPPER_CONFIG_DIR=$OPTARG
                break
            ;;
            [?]|h)
                echo -e "\nUsage: ${0} -c /path/to/klipper_config"
                exit 1
            ;;
        esac
    fi
    break
done

# Run steps

echo -e ""
echo -e "    ___  ___  __  __ "
echo -e "   | _ \/   \|  \/  |"
echo -e "   |  _/| - || |\/| |"
echo -e "   |_|  |_|_||_|  |_|"
echo -e ""
echo -e "Print Area Mesh for RatOS"
echo -e "v0.1.4"
echo -e ""
stop_klipper
create_macro_dir
link_macro
link_extra
start_klipper
echo -e "Installation finished!"
echo -e ""

# If something checks status of install
exit 0
