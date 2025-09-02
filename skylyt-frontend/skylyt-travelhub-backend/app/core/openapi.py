from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema excluding database models"""
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
    
    # Remove database model schemas from components
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas_to_remove = []
        for schema_name in openapi_schema["components"]["schemas"]:
            # Remove SQLAlchemy model schemas (typically have database-specific fields)
            if any(field in schema_name.lower() for field in ["model", "table", "db"]):
                schemas_to_remove.append(schema_name)
        
        for schema_name in schemas_to_remove:
            del openapi_schema["components"]["schemas"][schema_name]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema