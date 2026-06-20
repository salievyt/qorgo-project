from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Custom exception handler that formats errors consistently."""
    response = exception_handler(exc, context)

    if response is not None:
        # Format error response
        errors = response.data
        formatted_errors = {}

        if isinstance(errors, dict):
            for field, messages in errors.items():
                if isinstance(messages, list):
                    formatted_errors[field] = [str(m) for m in messages]
                else:
                    formatted_errors[field] = [str(messages)]
        elif isinstance(errors, list):
            formatted_errors = {'detail': [str(m) for m in errors]}
        else:
            formatted_errors = {'detail': [str(errors)]}

        response.data = {
            'success': False,
            'status_code': response.status_code,
            'errors': formatted_errors,
        }

    return response


class QorgoAPIException(Exception):
    """Base exception for Qorgo business logic errors."""

    def __init__(self, message, code='error', status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)
