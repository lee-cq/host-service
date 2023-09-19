import logging

logger = logging.getLogger("host-service.tools.gc_callback")


def gc_callback(phase, info):
    """GC回调函数"""
    if phase == "stop":
        logger.info(
            "GC 回收了 %d 个对象, 不可回收的对象: %d, 最久远的代: %d",
            info["collected"],
            info["uncollectable"],
            info["generation"],
        )
