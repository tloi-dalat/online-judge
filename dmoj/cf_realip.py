"""Restore the real client IP when TLOJ runs behind Cloudflare Tunnel.

Commit as dmoj/cf_realip.py. Enabled from .k8s.settings.py (PROXY__CLOUDFLARE).

Why: gunicorn sets REMOTE_ADDR to the immediate peer — the cloudflared pod —
and DMOJ reads REMOTE_ADDR directly in judge/user_log.py, the password-reset
throttle in judge/views/user.py, and via IP_BASED_AUTHENTICATION_HEADER.
Without this middleware every visitor appears to come from one address.

Trust model: the site Service is ClusterIP-only, so the only way in from outside
the cluster is through cloudflared, and Cloudflare overwrites CF-Connecting-IP at
its edge. If the site is ever exposed any other way (NodePort, LoadBalancer,
hostPort), this header becomes client-controlled: set PROXY__CLOUDFLARE=false.
"""
import ipaddress


class CloudflareRealIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('HTTP_CF_CONNECTING_IP', '').strip()
        if ip:
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                pass  # malformed: keep the peer address rather than store garbage
            else:
                request.META['REMOTE_ADDR'] = ip
        return self.get_response(request)
