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
