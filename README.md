
# Gluetun – Home Assistant Custom Integration

[![Validate](https://github.com/kramttocs/ha-gluetun/actions/workflows/validate.yaml/badge.svg)](https://github.com/kramttocs/ha-gluetun/actions/workflows/validate.yaml)
[![GitHub Release](https://img.shields.io/github/release/kramttocs/ha-gluetun.svg)](https://github.com/kramttocs/ha-gluetun/releases)
[![GitHub Activity](https://img.shields.io/github/commit-activity/m/kramttocs/ha-gluetun.svg)](https://github.com/kramttocs/ha-gluetun/commits/main)

A Home Assistant custom integration that retrieves data from, and minimally controls a Gluetun instance

The integration polls the Gluetun API every 60 seconds, while the public IP and settings refresh every 5 minutes.

This is/was designed, reviewed, and tested by me. AI assisted in generating documentation and some logic/design patterns.

---

# Acknowledgments

**qdm12** for the **Gluetun** project.

https://github.com/qdm12/gluetun

**madcowGIT** for the concept of this integration (and the 'ok' to promote mine)

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

## HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kramttocs&repository=ha-gluetun&category=integration)

# Requirements

A Gluetan instance with the **HTTP Control Server enabled**

Example control server address:

`http://<gluetun-host>:8000`

---
