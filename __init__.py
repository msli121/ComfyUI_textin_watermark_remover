from .textin_watermark_remover import TextinRemoveWatermark

NODE_CLASS_MAPPINGS = {
    "textin_remove_watermark": TextinRemoveWatermark
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "textin_remove_watermark": "Textin去水印"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']    