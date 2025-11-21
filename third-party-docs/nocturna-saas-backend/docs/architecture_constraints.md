# Architectural Constraints

## Calculation Server Architecture

### Core Principle
All astrological calculations MUST be performed by the external calculation server (nocturna-calculations). No calculations should be implemented directly in this project.

### Communication Protocol
- **Primary and Only**: REST API (http://localhost:8000)
- **Authentication**: Service tokens for secure API access

### Implementation Rules
1. **No Local Calculations**
   - Do not implement any calculation logic in this project
   - Do not add any calculation-related dependencies (e.g., Swiss Ephemeris)
   - Do not create calculation utility functions or classes

2. **Client-Server Pattern**
   - All calculations must go through the `CalculationClient`
   - Services should only handle request preparation and response formatting
   - No direct calculation logic in services

3. **REST API Communication**
   - Use HTTP POST requests for all calculation endpoints
   - Handle HTTP status codes properly (200, 401, 422, 500)
   - Implement proper authentication with service tokens
   - Use JSON request/response format

4. **Error Handling**
   - Use `CalculationError` for all calculation-related errors
   - Handle HTTP communication errors (timeouts, connection failures)
   - Implement proper error logging and user feedback
   - Handle 422 validation errors from calculation server

5. **Testing**
   - Test client-server communication, not calculation logic
   - Mock external calculation server responses
   - Test error handling scenarios (network failures, validation errors)
   - Test authentication and authorization

### Code Review Checklist
When reviewing code, ensure:
- [ ] No calculation logic is implemented locally
- [ ] All calculations use `CalculationClient` with REST API
- [ ] Proper HTTP error handling is in place
- [ ] Service token authentication is used
- [ ] Tests focus on communication, not calculations
- [ ] No WebSocket or async communication patterns

### Common Pitfalls to Avoid
1. Implementing calculation utilities
2. Adding calculation-related dependencies
3. Creating calculation-specific models (use schemas from calculation server)
4. Writing tests that assume local calculations
5. Adding calculation-specific configuration
6. Using deprecated WebSocket communication patterns

### Available Calculation Endpoints
The following REST endpoints are available via `CalculationClient`:
- `/api/calculations/planetary-positions` - Basic planetary positions
- `/api/calculations/secondary-progressions` - Secondary progressions
- `/api/calculations/aspects` - Planetary aspects
- `/api/calculations/houses` - House cusps calculation
- `/api/calculations/fixed-stars` - Fixed star positions
- `/api/calculations/arabic-parts` - Arabic parts/lots
- `/api/calculations/dignities` - Planetary dignities

### References
- [Calculation Client Implementation](../src/services/calculation_client.py)
- [Chart Service Implementation](../src/services/chart_service.py) 