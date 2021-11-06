import platform


def get_tag_address(mac, core_bluetooth):
    return (
        mac
        if platform.system() != "Darwin"
        else core_bluetooth
    )
