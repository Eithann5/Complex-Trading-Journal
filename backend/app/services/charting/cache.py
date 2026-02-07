from pathlib import Path
from typing import NamedTuple

from app.config import settings
from app.services.charting.profiles import ChartProfile


class ChartPathInfo(NamedTuple):
    absolute_path: Path
    static_url: str


def resolve_trigger_chart_path(
    *,
    trigger_id: str,
    symbol: str,
    profile: ChartProfile,
) -> ChartPathInfo:
    symbol_clean = symbol.upper().strip()
    filename = f"{trigger_id}_{profile.filename_suffix}.png"

    relative_parts = [profile.output_subdirectory]
    if profile.include_symbol_subdir:
        relative_parts.append(symbol_clean)
    relative_parts.append(filename)

    relative_path = Path(*relative_parts)
    absolute_path = settings.data_dir / relative_path
    static_url = f"/static/{relative_path.as_posix()}"
    return ChartPathInfo(absolute_path=absolute_path, static_url=static_url)


def chart_exists(path: Path) -> bool:
    return path.is_file()


def ensure_output_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def assert_no_overwrite(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Chart file already exists: {path}")
