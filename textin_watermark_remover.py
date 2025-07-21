import requests
import base64
import os
import tempfile
from PIL import Image
import folder_paths
import logging
import torch
import numpy as np

# 配置日志
logger = logging.getLogger("comfyui-textin-watermark")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
                "image": ("IMAGE",)
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "remove_watermark"
    CATEGORY = "image/postprocessing"
    
    def remove_watermark(self, api_id, api_code, image):
        """
        调用Textin API去除图片水印
        """
        if not api_id or not api_code:
            logger.error("API ID和API Code不能为空")
            return (image,)
        
        # 将张量转换为PIL图像
        pil_image = self._tensor_to_pil(image)
        
        # 创建临时文件
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.png")
            pil_image.save(input_path, "PNG")
            
            # 调用API
            output_image = self._call_watermark_api(api_id, api_code, input_path)
            
            if output_image:
                # 转换回张量
                output_tensor = self._pil_to_tensor(output_image)
                return (output_tensor,)
        
        # 如果出错，返回原始图像
        return (image,)
    
    def _call_watermark_api(self, api_id, api_code, img_path):
        """
        调用Textin去水印API
        """
        url = "https://api.textin.com/ai/service/v1/image/watermark_remove"
        
        try:
            with open(img_path, 'rb') as img_file:
                img_data = img_file.read()
                
            headers = {
                "Content-Type": "application/octet-stream",
                "x-ti-app-id": api_id,
                "x-ti-secret-code": api_code
            }
            
            response = requests.post(url, headers=headers, data=img_data)
            response.raise_for_status()
            
            response_json = response.json()
            if response_json.get("code") == 200:
                base64_image = response_json["result"].get("image")
                if base64_image:
                    img_data = base64.b64decode(base64_image)
                    return Image.open(io.BytesIO(img_data))
                else:
                    logger.error("响应中未找到图像数据")
            else:
                logger.error(f"API错误: {response_json.get('message')}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {str(e)}")
        except Exception as e:
            logger.error(f"处理异常: {str(e)}")
            
        return None
    
    def _tensor_to_pil(self, tensor):
        """将张量转换为PIL图像"""
        tensor = tensor.cpu().clone()
        tensor = tensor.squeeze(0)
        tensor = tensor.permute(1, 2, 0)
        tensor = (tensor * 255).round().clamp(0, 255).to(torch.uint8).numpy()
        return Image.fromarray(tensor)
    
    def _pil_to_tensor(self, image):
        """将PIL图像转换为张量"""
        img = np.array(image).astype(np.float32) / 255.0
        img = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
        return img    