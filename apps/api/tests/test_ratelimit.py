from hackproof.chat.ratelimit import HOUR, MINUTE, RateLimiter


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_allows_ten_a_minute_then_denies():
    clock = Clock()
    limiter = RateLimiter(clock=clock)
    assert all(limiter.check("a") is None for _ in range(10))
    denied = limiter.check("a")
    assert denied is not None
    assert (denied.window, denied.limit) == ("minute", 10)
    assert denied.retry_after == 60


def test_minute_window_recovers():
    clock = Clock()
    limiter = RateLimiter(clock=clock)
    for _ in range(10):
        limiter.check("a")
    clock.now = 61
    assert limiter.check("a") is None


def test_hour_window_caps_at_fifty():
    clock = Clock()
    limiter = RateLimiter(clock=clock)
    for _ in range(50):
        assert limiter.check("a") is None
        clock.now += 61
    clock.now = 50 * 61 - 61 + 1
    denied = limiter.check("a")
    assert denied is not None
    assert denied.window == "hour"
    assert denied.retry_after > 60


def test_clients_are_independent():
    limiter = RateLimiter(windows=(MINUTE,))
    for _ in range(10):
        limiter.check("a")
    assert limiter.check("a") is not None
    assert limiter.check("b") is None


def test_denied_requests_do_not_extend_the_window():
    clock = Clock()
    limiter = RateLimiter(windows=(MINUTE, HOUR), clock=clock)
    for _ in range(10):
        limiter.check("a")
    clock.now = 30
    assert limiter.check("a") is not None
    clock.now = 61
    assert limiter.check("a") is None
