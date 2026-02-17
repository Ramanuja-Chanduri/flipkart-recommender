import sys

class CustomException(Exception):
    def __init__(self, message: str, error_detail: Exception):
        self.error_message = self.get_detailed_error_message(error_detail)
        super().__init__(self.error_message)

    @staticmethod
    def get_detailed_error_message(error: Exception) -> str:
        _, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        return f"Error occurred in file: {file_name} at line: {line_number} with message: {str(error)}"
    
    def __str__(self):
        return self.error_message