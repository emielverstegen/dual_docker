def classFactory(iface):
    from .dual_docker import DualDocker
    return DualDocker(iface)


# any other initialisation needed