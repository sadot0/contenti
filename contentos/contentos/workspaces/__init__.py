from contentos.workspaces.instagram import INSTAGRAM
from contentos.workspaces.tiktok import TIKTOK
from contentos.workspaces.youtube import YOUTUBE

WORKSPACES = {"instagram": INSTAGRAM, "tiktok": TIKTOK, "youtube": YOUTUBE}


def get_workspace(network: str):
    if network not in WORKSPACES:
        raise ValueError(f"Неизвестная соцсеть: {network}. Доступно: {list(WORKSPACES)}")
    return WORKSPACES[network]
