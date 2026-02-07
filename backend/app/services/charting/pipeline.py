from typing import Any

from app.services.charting.cache import (
    assert_no_overwrite,
    chart_exists,
    ensure_output_directory,
    resolve_trigger_chart_path,
)
from app.services.charting.profiles import get_profile
from app.services.charting.renderer import render_trigger_chart


def get_trigger_chart_url(trigger: Any, profile: str = "alert_basic") -> str:
    chart_profile = get_profile(profile)
    path_info = resolve_trigger_chart_path(
        trigger_id=str(trigger.trigger_id),
        symbol=str(trigger.symbol),
        profile=chart_profile,
    )
    return path_info.static_url


def has_trigger_chart(trigger: Any, profile: str = "alert_basic") -> bool:
    chart_profile = get_profile(profile)
    path_info = resolve_trigger_chart_path(
        trigger_id=str(trigger.trigger_id),
        symbol=str(trigger.symbol),
        profile=chart_profile,
    )
    return chart_exists(path_info.absolute_path)


def ensure_trigger_chart(trigger: Any, profile: str = "alert_basic") -> str:
    chart_profile = get_profile(profile)
    path_info = resolve_trigger_chart_path(
        trigger_id=str(trigger.trigger_id),
        symbol=str(trigger.symbol),
        profile=chart_profile,
    )

    if chart_exists(path_info.absolute_path):
        return path_info.static_url

    ensure_output_directory(path_info.absolute_path)
    assert_no_overwrite(path_info.absolute_path)
    try:
        render_trigger_chart(trigger, chart_profile, path_info.absolute_path)
    except Exception:  # noqa: BLE001
        if path_info.absolute_path.exists():
            path_info.absolute_path.unlink()
        raise
    return path_info.static_url
