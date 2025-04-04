#!/bin/bash

# Function to install dependencies on Arch-based systems
install_arch() {

	echo "[+] Arch based OS detected, installing via pacman..."
	# Update package list and install dependencies system-wide
	sudo pacman -Sy python-requests python-tqdm python-urllib3
	echo "[+] Dependency install finished"

}

#Function to install dependencies on Debian-based systems
install_debian() {
	
	echo "[+] Debian based OS detected, installing via apt..."
	#Install systemwide packaged
	sudo apt install -y python3-requests python3-tqdm python3-urllib3
	echo "[+] Dependecy install finished"
}

# Check the OS type
if [[ -f /etc/os-release ]]; then
	source /etc/os-release

	if [[ "$ID" == "arch" || "$ID_LIKE" == *"arch"* ]]; then
		install_arch
	elif [[ "$ID" == "debian" || "$ID_LIKE" == *"debian"* ]]; then
		install_debian
	else
		echo "[!] Unsupported OS: Please install via pip"
		exit 1
	fi
else
	echo "[!] Could not determine OS via /etc/os-release, please install via pip"
	exit 1
fi

echo "[+] System-wide install finished"
