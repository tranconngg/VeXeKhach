import re
from typing import Tuple

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Kiểm tra độ mạnh của mật khẩu
    Yêu cầu:
    - Tối thiểu 8 ký tự
    - Có ít nhất 1 chữ hoa
    - Có ít nhất 1 chữ thường
    - Có ít nhất 1 số
    - Có ít nhất 1 ký tự đặc biệt
    """
    if len(password) < 8:
        return False, "Mật khẩu phải có ít nhất 8 ký tự"
    
    if not re.search(r"[A-Z]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ hoa"
    
    if not re.search(r"[a-z]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 chữ thường"
    
    if not re.search(r"\d", password):
        return False, "Mật khẩu phải chứa ít nhất 1 số"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt"
    
    return True, "Mật khẩu hợp lệ"

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Kiểm tra tính hợp lệ của username
    Yêu cầu:
    - Độ dài từ 3-20 ký tự
    - Chỉ chứa chữ cái, số và dấu gạch dưới
    - Bắt đầu bằng chữ cái
    """
    if not (3 <= len(username) <= 20):
        return False, "Username phải có độ dài từ 3-20 ký tự"
    
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username):
        return False, "Username chỉ được chứa chữ cái, số và dấu gạch dưới, và phải bắt đầu bằng chữ cái"
    
    return True, "Username hợp lệ" 