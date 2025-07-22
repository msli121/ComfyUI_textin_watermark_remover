import base64
import io
import logging
import os
import tempfile

import requests
import torchvision.transforms.functional as F
from PIL import Image

# 配置日志
logger = logging.getLogger("comfyui-textin-watermark")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class TextinRemoveWatermark:
    """
    ComfyUI节点：调用Textin API去除图片水印
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_id": ("STRING", {"multiline": False, "default": ""}),
                "api_code": ("STRING", {"multiline": False, "default": ""}),
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "remove_watermark"
    CATEGORY = "image/postprocessing"

    def remove_watermark(self, api_id, api_code, image):
        """
        调用Textin API去除图片水印
        """
        if not api_id or not api_code:
            logger.error("API ID和API Code不能为空")
            return (image,)
        if image is None:
            logger.error("输入图像不能为空")
            return (image,)

        # 检查并调整shape
        if image.ndim == 4:
            # (B, C, H, W) 或 (B, H, W, C)
            if image.shape[1] in [1, 3, 4]:  # (B, C, H, W)
                img_tensor = image[0]
            elif image.shape[-1] in [1, 3, 4]:  # (B, H, W, C)
                img_tensor = image[0].permute(2, 0, 1)
            else:
                logger.error(f"未知的图片shape: {image.shape}")
                return (image,)
        elif image.ndim == 3:
            # (C, H, W) 或 (H, W, C)
            if image.shape[0] in [1, 3, 4]:  # (C, H, W)
                img_tensor = image
            elif image.shape[-1] in [1, 3, 4]:  # (H, W, C)
                img_tensor = image.permute(2, 0, 1)
            else:
                logger.error(f"未知的图片shape: {image.shape}")
                return (image,)
        else:
            logger.error(f"未知的图片shape: {image.shape}")
            return (image,)

        # 转为PIL
        pil_image = F.to_pil_image(img_tensor)

        # 创建临时文件
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.png")
            pil_image.save(input_path, "PNG")

            # 调用API
            output_image = self._call_watermark_api(api_id, api_code, input_path)

            if output_image:
                # 转换回张量，转为 float32 类型，除以 255，并限制在 0～1 之间
                output_tensor = F.to_tensor(output_image).unsqueeze(0).float()
                # 调整维度顺序为 [1, H, W, C]
                output_tensor = output_tensor.permute(0, 2, 3, 1)
                logger.info(f"output_tensor shape: {output_tensor.shape} type: {output_tensor.dtype} min: {output_tensor.min()} max: {output_tensor.max()}")
                return (output_tensor,)

        # 如果出错，返回原始图像
        return (image,)

    def _call_watermark_api(self, api_id, api_code, img_path):
        """
        调用Textin去水印API
        """
        url = "https://api.textin.com/ai/service/v1/image/watermark_remove"

        try:
            with open(img_path, "rb") as img_file:
                img_data = img_file.read()

            headers = {
                "Content-Type": "application/octet-stream",
                "x-ti-app-id": api_id,
                "x-ti-secret-code": api_code,
            }
            logger.info(f"调用Textin去水印API, api_id: {api_id}, api_code: {api_code}, img_path: {img_path}")
            response = requests.post(url, headers=headers, data=img_data)
            response.raise_for_status()

            response_json = response.json()
            if response_json.get("code") == 200:
                base64_image = response_json["result"].get("image")
                if base64_image:
                    img_data = base64.b64decode(base64_image)
                    pil_image = Image.open(io.BytesIO(img_data))
                    logger.info(f"pil image size: {pil_image.width}x{pil_image.height}")
                    return pil_image
                else:
                    logger.error("响应中未找到图像数据")
            else:
                logger.error(f"API错误: {response_json.get('message')}")

        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {str(e)}")
        except Exception as e:
            logger.error(f"处理异常: {str(e)}")

        return None
