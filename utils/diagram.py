import zlib
import base64

def deflate_and_base64_encode(data):
    # 使用zlib进行deflate压缩
    compressed_data = zlib.compress(data, level=9)
    # 使用base64进行编码
    encoded_data = base64.b64encode(compressed_data)
    return encoded_data

def base64_decode_and_inflate(encoded_data):
    # 使用base64进行解码
    compressed_data = base64.b64decode(encoded_data)
    # 使用zlib进行inflate解压缩
    data = zlib.decompress(compressed_data)
    return data

def get_plantuml_diagram(text):
    return get_common_diagram(text, diagram_type="plantuml")

def get_common_diagram(text, diagram_type, image_format="svg"):
    if not isinstance(text, bytes):
        text = text.encode('utf-8')
    original_data = text
    encoded_data = deflate_and_base64_encode(original_data)
    url_param = encoded_data.decode("utf-8").replace("/", "_").replace("+", "-")
    return f"https://kroki.io/{diagram_type}/{image_format}/{url_param}"
