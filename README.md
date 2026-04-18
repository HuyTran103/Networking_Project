# \# Homelab Documentation

# 

###### A collection of setup guides for self-hosted services and network security

###### based on my personal homelab experience.

###### 

###### \---

###### 

###### \## Documents

###### 

###### \### Setting Up and Securing Ubuntu Server as a Tailscale Exit Node

###### Step-by-step guide to configuring an Ubuntu server as a Tailscale exit node,

###### with firewall hardening to prevent public exposure once the server is on the internet.

###### \- Install Tailscale and enable IP forwarding to advertise as exit node

###### \- Set up UFW firewall — restrict SSH, Jellyfin, Samba, and Home Assistant

###### &#x20; to Tailscale and local network only, not open to the internet

###### \- SSH key authentication setup to replace password login

###### \- \*\*⚠️ Important:\*\* Once exit node is enabled, your server is exposed to the

###### &#x20; internet — firewall hardening in this guide is essential, not optional

###### 

###### \---

###### 

###### \### Setting Up Pi-hole in Raspberry Pi Zero 2 W

###### Installation guide for Pi-hole on a Raspberry Pi Zero 2 W as a network-wide

###### ad blocker, with DNS configuration for individual devices.

###### \- Flash Raspberry Pi OS Lite and install Pi-hole via terminal

###### \- Reserve a static IP via router DHCP for a stable DNS server

###### \- Cloudflare (1.1.1.1) recommended over Google DNS for speed and privacy

###### \- Configure DNS manually on iPhone and Windows to point to Pi-hole

###### \- Includes troubleshooting section covering DNS tests, WiFi stability,

###### &#x20; and channel congestion diagnosis

###### \- \*\*⚠️ Important:\*\* Enable "Permit all origins" in Pi-hole DNS settings —

###### &#x20; required for Tailscale integration to work properly

###### 

###### \---

###### 

###### \### Setting Up Pi-hole with Tailscale

###### Guide to integrating Pi-hole with Tailscale so that ad-blocking applies

###### to all your devices anywhere, not just when you're home.

###### \- Install Tailscale on the Pi-hole server with `--accept-dns=false`

###### &#x20; to prevent Tailscale from overriding Pi-hole as the DNS server

###### \- Add Pi-hole's Tailscale IP as a custom nameserver in the Tailscale

###### &#x20; admin console with "Use with exit node" enabled

###### \- Includes Tailscale account reset and reinstall steps if needed

###### \- Pi-hole maintenance commands included (flush DNS, update gravity,

###### &#x20; toggle on/off, check status)

###### \- \*\*⚠️ Important:\*\* Use `--accept-dns=false` when bringing up Tailscale,

###### &#x20; otherwise Tailscale will override Pi-hole's DNS

###### 

###### \---

###### 

###### \### Adding Security Layer for Pi-hole Server

###### Covers hardening the Pi-hole server with iptables firewall rules to lock

###### down DNS and web interface access to trusted sources only.

###### \- Restrict port 53 (DNS) and port 80 (Pi-hole web UI) to Tailscale

###### &#x20; (100.64.0.0/10) and local network (192.168.1.0/24) only

###### \- Drop all other incoming traffic to prevent public DNS abuse

###### \- Rules are saved with `iptables-persistent` to survive reboots

###### \- Troubleshooting section included to flush and re-add rules if order breaks

###### \- \*\*⚠️ Important:\*\* Rule order matters 

