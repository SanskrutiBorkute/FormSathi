import logging

class FormSathiError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class EmptyImageError(FormSathiError):
    def __init__(self, message="Image is empty. Please upload a valid form image."):
        super().__init__(message, 400)

class BlurryImageError(FormSathiError):
    def __init__(self, message="Image quality is too low. Please upload a clearer image."):
        super().__init__(message, 400)

class OCRFailureError(FormSathiError):
    def __init__(self, message="No fields could be detected from this form."):
        super().__init__(message, 422)

class UnsupportedFormError(FormSathiError):
    def __init__(self, message="This form format is currently unsupported."):
        super().__init__(message, 400)

class AIGuidanceError(FormSathiError):
    def __init__(self, message="AI guidance translation failed. Please try again."):
        super().__init__(message, 500)

class ValidationError(FormSathiError):
    def __init__(self, message="Field validation failed due to structural rule conflicts."):
        super().__init__(message, 400)

class ExportError(FormSathiError):
    def __init__(self, message="Export failed. Unable to generate summary document."):
        super().__init__(message, 500)

def register_error_handlers(app):
    @app.errorhandler(FormSathiError)
    def handle_formsathi_error(error):
        # Return structured JSON with friendly error text
        return {"message": error.message}, error.status_code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        # Log stack trace in the background/console for debugging
        logging.exception(f"Unhandled Exception encountered: {str(error)}")
        # Do not expose stack traces. Return a simple message.
        return {"message": "An unexpected server error occurred. Please try again later."}, 500
