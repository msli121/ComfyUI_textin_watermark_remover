# ComfyUI_textin_remove_watermark

这是一个用于ComfyUI的自定义节点，可调用Textin的去水印API接口去除图片水印。

## 功能说明

该节点允许你通过Textin的API服务去除图片中的水印，支持将处理后的图片集成到你的ComfyUI工作流中。

## 安装方法

1. 打开你的ComfyUI安装目录
2. 进入`custom_nodes`文件夹
3. 克隆本项目：`git clone https://github.com/yourusername/ComfyUI_textin_remove_watermark.git`
4. 安装依赖：`pip install requests pillow`
5. 重启ComfyUI

## 使用方法

1. 在ComfyUI界面中，从节点列表中找到"Textin去水印"节点
2. 输入你的Textin API ID和API Code
3. 连接需要去水印的图片
4. 执行工作流，节点将输出去水印后的图片

## 节点参数

- `api_id`: 你的Textin API ID
- `api_code`: 你的Textin API Code
- `image`: 需要去水印的输入图片

## 注意事项

- 使用本节点需要有效的Textin API凭证
- API调用可能会产生费用，请查看Textin官方文档了解详情
- 处理时间取决于API响应速度和图片复杂度
- 节点默认在出错时返回原始图片

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。
    