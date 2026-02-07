from typing import Any

from app.services.charting.cache import (
    assert_no_overwrite,
    chart_exists,
    ensure_output_directory,
    resolve_trigger_chart_path,
)
from app.services.charting.profiles import get_profile
from app.services.charting.renderer import render_trigger_chart


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
    render_trigger_chart(trigger, chart_profile, path_info.absolute_path)
    return path_info.static_url
