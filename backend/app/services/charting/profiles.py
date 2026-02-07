from dataclasses import dataclass


@dataclass(frozen=True)
class RenderOptions:
    figsize: tuple[float, float]
    dpi: int
    show_volume: bool
    show_title: bool
    tight_layout: bool


@dataclass(frozen=True)
class ChartProfile:
    name: str
    lookback_days: int
    data_period: str
    data_interval: str
    indicators: tuple[str, ...]
    output_subdirectory: str
    filename_suffix: str
    include_symbol_subdir: bool
    render: RenderOptions


CHART_PROFILES: dict[str, ChartProfile] = {
    "alert_basic": ChartProfile(
        name="alert_basic",
        lookback_days=60,
        data_period="2y",
        data_interval="1d",
        indicators=("sma_20", "sma_150", "sma_200"),
        output_subdirectory="charts/triggers",
        filename_suffix="alert_basic_v1",
        include_symbol_subdir=True,
        render=RenderOptions(
            figsize=(12, 6),
            dpi=200,
            show_volume=False,
            show_title=False,
            tight_layout=True,
        ),
    ),
    "position_advanced": ChartProfile(
        name="position_advanced",
        lookback_days=252,
        data_period="2y",
        data_interval="1d",
        indicators=(),
        output_subdirectory="charts/positions",
        filename_suffix="position_advanced_v1",
        include_symbol_subdir=False,
        render=RenderOptions(
            figsize=(16, 9),
            dpi=200,
            show_volume=True,
            show_title=False,
            tight_layout=True,
        ),
    ),
}


def get_profile(profile_name: str) -> ChartProfile:
    profile = CHART_PROFILES.get(profile_name)
    if profile is None:
        raise ValueError(f"Unknown chart profile: {profile_name}")
    return profile
