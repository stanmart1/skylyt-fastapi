from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi(app: FastAPI):
    """Generate comprehensive OpenAPI schema with enhanced documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        contact=app.contact,
        license_info=app.license_info,
    )
    
    # Enhanced API information
    openapi_schema["info"].update({
        "contact": {
            "name": "Skylyt API Support",
            "email": "support@skylyt.com",
            "url": "https://skylyt.com/support"
        },
        "termsOfService": "https://skylyt.com/terms",
        "x-logo": {
            "url": "https://skylyt.com/logo.png",
            "altText": "Skylyt Logo"
        }
    })
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /auth/login endpoint"
        }
    }
    
    # Add common response schemas
    openapi_schema["components"]["schemas"].update({
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "description": "Error message"},
                "error_code": {"type": "string", "description": "Error code for programmatic handling"}
            },
            "required": ["detail"]
        },
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Success message"},
                "data": {"type": "object", "description": "Response data"}
            },
            "required": ["message"]
        },
        "PaginatedResponse": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {}, "description": "List of items"},
                "total": {"type": "integer", "description": "Total number of items"},
                "page": {"type": "integer", "description": "Current page number"},
                "per_page": {"type": "integer", "description": "Items per page"},
                "total_pages": {"type": "integer", "description": "Total number of pages"}
            },
            "required": ["items", "total", "page", "per_page", "total_pages"]
        }
    })
    
    # Add common response examples
    openapi_schema["components"]["examples"] = {
        "ValidationError": {
            "summary": "Validation Error",
            "value": {
                "detail": "Validation failed",
                "errors": [{"field": "email", "message": "Invalid email format"}]
            }
        },
        "NotFoundError": {
            "summary": "Resource Not Found",
            "value": {"detail": "Resource not found"}
        },
        "UnauthorizedError": {
            "summary": "Unauthorized Access",
            "value": {"detail": "Authentication required"}
        }
    }
    
    # Remove database model schemas from components
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas_to_remove = []
        for schema_name in openapi_schema["components"]["schemas"]:
            if any(field in schema_name.lower() for field in ["model", "table", "db"]):
                schemas_to_remove.append(schema_name)
        
        for schema_name in schemas_to_remove:
            del openapi_schema["components"]["schemas"][schema_name]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema