# Private DNS

This module provides private DNS resolution for the project.

DNS Server:
- Host: Mac 1
- Software: dnsmasq
- Protocol: DNS over UDP
- Port: 53

Private domain:
- app.team1.test
- api.team1.test

Both names resolve to the private IP address of the nginx/edge server.