"""Safe provider failures / 不泄露密钥或材料的服务失败说明。"""
import httpx


def ai_failure_reason(error):
    if isinstance(error, httpx.TimeoutException):
        return "the OpenAI request timed out; please try again"
    if isinstance(error, httpx.HTTPStatusError):
        response = error.response
        try:
            detail = response.json().get("error") or {}
            code = detail.get("code")
        except (ValueError, AttributeError, TypeError):
            code = None
        if response.status_code == 401:
            return "OpenAI rejected the API key; update it and restart the server"
        if response.status_code == 403:
            return "the API project does not have permission for this request"
        if response.status_code == 429:
            if code in {"insufficient_quota", "billing_hard_limit_reached", "organization_usage_limit_exceeded"}:
                return "the API project has no available quota; check its billing or usage limit"
            return "OpenAI rate-limited the request; wait briefly and try again"
        if response.status_code == 404:
            return "the configured model is unavailable to this API project"
        if response.status_code >= 500:
            return "OpenAI is temporarily unavailable; please try again"
        return "OpenAI rejected the request configuration"
    if isinstance(error, httpx.TransportError):
        return "the server could not connect to OpenAI; check its network or proxy access"
    return "OpenAI returned an incomplete or unreadable response"
