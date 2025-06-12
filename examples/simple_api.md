# Simple REST API Specification

Build a simple REST API for a todo list application.

## Requirements

### Core Features
- RESTful endpoints for CRUD operations
- In-memory data storage
- JSON request/response format
- Basic input validation

### Endpoints
- GET /todos - List all todos
- GET /todos/{id} - Get a specific todo
- POST /todos - Create a new todo
- PUT /todos/{id} - Update a todo
- DELETE /todos/{id} - Delete a todo

### Data Model
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Technical Requirements
- Use FastAPI framework
- Include OpenAPI documentation
- Add basic error handling
- Implement request validation
- No authentication required

### Acceptance Criteria
- All endpoints return appropriate status codes
- Invalid requests return 400 with error details
- Non-existent resources return 404
- Server errors return 500
- API documentation accessible at /docs