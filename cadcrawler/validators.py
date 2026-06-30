"""
文件验证器
"""

import os


# 文件签名
SIGNATURES = {
    'dxf': [
        b'  0\nSECTION',
        b'  0\r\nSECTION',
        b'0\nSECTION',
        b'0\r\nSECTION',
        b'$ACADVER',
        b'$DWGCODEPAGE',
    ],
    'stl_ascii': [b'solid '],
    'step': [b'ISO-10303-21', b'HEADER', b'FILE_SCHEMA'],
    'svg': [b'<svg', b'<?xml', b'<!DOCTYPE svg'],
}


def validate_dxf(filepath: str) -> bool:
    """验证DXF文件"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(500)
            for sig in SIGNATURES['dxf']:
                if sig in header:
                    return True
        return False
    except:
        return False


def validate_stl(filepath: str) -> bool:
    """验证STL文件"""
    try:
        size = os.path.getsize(filepath)
        if size < 84:
            return False

        with open(filepath, 'rb') as f:
            header = f.read(100)
            # ASCII STL
            for sig in SIGNATURES['stl_ascii']:
                if header.startswith(sig):
                    return True
            # Binary STL: 检查大小是否合理 (84字节头 + 50字节/三角形)
            # 只要不是太小且不是明显无效的文本就算通过
            return not header.startswith(b'<') and not header.startswith(b'{')
    except:
        return False


def validate_step(filepath: str) -> bool:
    """验证STEP文件"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(500)
            for sig in SIGNATURES['step']:
                if sig in header:
                    return True
        return False
    except:
        return False


def validate_svg(filepath: str) -> bool:
    """验证SVG文件"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(200).lower()
            for sig in SIGNATURES['svg']:
                if sig in header:
                    return True
        return False
    except:
        return False


def validate_file(filepath: str, ext: str = None) -> bool:
    """通用文件验证"""
    if ext is None:
        ext = os.path.splitext(filepath)[1].lower()

    if ext == '.dxf':
        return validate_dxf(filepath)
    elif ext == '.stl':
        return validate_stl(filepath)
    elif ext in ('.step', '.stp'):
        return validate_step(filepath)
    elif ext == '.svg':
        return validate_svg(filepath)

    # 其他类型不做严格验证，只要不是空文件
    try:
        return os.path.getsize(filepath) > 0
    except:
        return False
