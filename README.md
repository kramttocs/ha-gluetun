
# Gluetun – Home Assistant Custom Integration

[![License](https://img.shields.io/github/license/kramttocs/ha-gluetun.svg)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/kramttocs/ha-gluetun/actions/workflows/validate.yaml/badge.svg)](https://github.com/kramttocs/ha-gluetun/actions/workflows/validate.yaml)
[![GitHub Release](https://img.shields.io/github/release/kramttocs/ha-gluetun.svg)](https://github.com/kramttocs/ha-gluetun/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/m/kramttocs/ha-gluetun.svg)](https://github.com/kramttocs/ha-gluetun/commits/main)

This is a **Home Assistant custom integration** that retrieves data from, and minimally controls a Gluetun instance

The integration polls the Gluetun API every **60 seconds**, while the **public IP and settings refresh every 5 minutes**.

This is/was designed, reviewed, and tested by me. AI assisted in generating documentation and some logic/design patterns.

---

# Acknowledgments

**qdm12** for the **Gluetun** project.

https://github.com/qdm12/gluetun

**madcowGIT** for the concept of this integraton

https://github.com/madcowGit/gluetun_cc

---

# Features

### Sensors

| Sensor | Source Endpoint |
|------|------|
| VPN Status | `/v1/vpn/status` |
| Public IP | `/v1/publicip/ip` |

### Device Information

The integration dynamically sets the device metadata using:

| Field | Value |
|------|------|
| Manufacturer | `provider.name` from `/v1/vpn/settings` |
| Model | `type` from `/v1/vpn/settings` |

Example:

Manufacturer: **Private Internet Access**  
Model: **openvpn**

### Buttons

| Button | Action |
|------|------|
| Start VPN | `PUT /v1/vpn/status` with `"running"` |
| Stop VPN | `PUT /v1/vpn/status` with `"stopped"` |

---

# Installation

## HACS (Recommended)

1. Open **HACS**
2. Navigate to **Integrations**
3. Click the **⋯ (three dots)** menu
4. Select **Custom repositories**
5. Add:

https://github.com/kramttocs/ha-gluetun

Repository type: **Integration**

6. Click **Add**
7. Search for **Gluetun**
8. Click **Install**
9. Restart Home Assistant

---

## Manual Installation

1. Download or clone this repository.
2. Copy:

`custom_components/gluetun`

into your Home Assistant configuration directory:

`config/custom_components/`

Example:

config/
└── custom_components/
    └── gluetun/

3. Restart Home Assistant.

---

# Requirements

A Gluetan instance with the **HTTP Control Server enabled**

Example control server address:

`http://<gluetun-host>:8000`

Authentication must also be enabled because the integration uses **HTTP Basic Authentication**. 

Other Gluetun authentication types will be added shortly.

---

# Configuration (Home Assistant)

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Gluetun**
4. Enter:

| Field | Description |
|------|------|
| Host | IP or hostname of your Gluetun instance |
| Port | Control server port (default 8000) |
| SSL | Enable if using HTTPS |
| Verify SSL | Disable for self-signed certificates |
| Username | Control server username |
| Password | Control server password |

5. Finish the setup.

Entities will automatically be created.

---

# Entities Created

### Sensors

sensor.gluetun_vpn_status  
sensor.gluetun_public_ip

### Buttons

button.gluetun_start_vpn  
button.gluetun_stop_vpn

