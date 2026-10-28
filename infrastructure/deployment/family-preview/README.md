# Friends-and-family preview candidate

This is an uninstalled candidate for an invited synthetic demo, not a production live pilot. The owner requested a shareable test by 5pm. Provider access, price, coverage and a lawful operational boundary are not verified. LIVE must remain disabled and every test record must remain clearly labelled synthetic. No real evidence, personal information, passwords or API keys should be submitted.

The candidate Caddy file uses HTTPS and a single shared preview credential, proxies only to a loopback web listener, requires same-origin unsafe requests, strips credentials before proxying, limits body size, and blocks evidence uploads. A shared password is not individual identity, audit attribution or isolation; testers share demo state. Protect it outside Git and chat. Before any exposure verify DNS and HTTPS certificates, upstream/API port bindings, the exact proxy configuration, inbound firewall rules and recovery, test unauthenticated rejection and allowed demo workflows, and ensure no other existing service is affected. Never reuse the SSH-tunnel HTTP-only gateway for a public preview.

Deployment is contingent on the owner accepting a synthetic fallback if the verified live feed cannot be ready. This document alone does not establish security, a working URL, deployment or source activation. Do not add paid services without owner approval.
