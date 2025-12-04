# Design Document: User Registration Feature

## Overview

The user registration feature extends the Events API to support user profiles and event registrations with capacity management. The design introduces a composite key schema (PK/SK) for DynamoDB to enable flexible querying patterns and follows single-table design principles. The system manages user registrations with capacity constraints, waitlist functionality, and automatic promotion of waitlisted users when spots become available.

Key capabilities:
- User profile creation and management
- Event registration with capacity enforcement
- Waitlist management with automatic promotion
- User registration listing
- Composite key schema migration for existing events

## Architecture

### High-Level Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  DynamoDB    │
│  (Browser)  │      │  (REST API)  │      │  (FastAPI)  │      │ (Single Table)│
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

The architecture maintains the existing serverless pattern while extending the data model to support multiple entity types in a single DynamoDB table using composite keys.

### Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│  User Routes    │  Event Routes  │  Registration Routes     │
│  /users         │  /events       │  /registrations          │
└────────┬────────┴────────┬───────┴──────────┬───────────────┘
         │                 │                  │
         ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  UserService    │  EventService  │  RegistrationService     │
└────────┬────────┴────────┬───────┴──────────┬───────────────┘
         │                 │                  │
         └─────────────────┴──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database Layer                              │
│  - Composite key operations (PK/SK)                          │
│  - Conditional writes for consistency                        │
│  - Query and scan operations                                 │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DynamoDB Table                            │
│  PK (Partition Key)  │  SK (Sort Key)  │  Attributes        │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Data Access Layer

**Purpose**: Abstracts DynamoDB operations with composite key support

**Key Functions**:
- `put_item(pk, sk, attributes)` - Store entity with composite key
- `get_item(pk, sk)` - Retrieve entity by composite key
- `query(pk, sk_prefix)` - Query items by partition key and sort key prefix
- `delete_item(pk, sk)` - Remove entity
- `conditional_put(pk, sk, attributes, condition)` - Atomic write with condition
- `transact_write(items)` - Atomic multi-item transaction

### 2. User Service

**Purpose**: Manages user profile operations

**Endpoints**:
- `POST /users` - Create user profile
- `GET /users/{userId}` - Retrieve user profile
- `GET /users/{userId}/registrations` - List user's event registrations

**Key Operations**:
- Create user with uniqueness validation
- Retrieve user profile
- List user registrations with event details

### 3. Event Service (Extended)

**Purpose**: Manages events with capacity and waitlist configuration

**Extended Attributes**:
- `capacity` (existing) - Maximum number of confirmed registrations
- `waitlistEnabled` (new) - Boolean flag for waitlist support

**Key Operations**:
- Migrate existing events to composite key schema
- Support capacity and waitlist configuration

### 4. Registration Service

**Purpose**: Manages event registrations with capacity enforcement

**Endpoints**:
- `POST /events/{eventId}/register` - Register user for event
- `DELETE /events/{eventId}/register/{userId}` - Unregister user from event
- `GET /events/{eventId}/registrations` - List event registrations

**Key Operations**:
- Register user with capacity check
- Add to waitlist when at capacity
- Unregister user and promote from waitlist
- Count confirmed registrations
- Query registrations by event or user

## Data Models

### Composite Key Schema

All entities use a composite key pattern with partition key (PK) and sort key (SK):

| Entity Type | PK Format | SK Format | Purpose |
|-------------|-----------|-----------|---------|
| User Profile | `USER#{userId}` | `PROFILE` | Store user information |
| Event Metadata | `EVENT#{eventId}` | `METADATA` | Store event information |
| Registration | `USER#{userId}` | `EVENT#{eventId}` | Store user-event registration |
| Event Registration Index | `EVENT#{eventId}` | `USER#{userId}` | Query registrations by event |

### User Model

```python
class User(BaseModel):
    userId: str          # Unique identifier
    name: str           # User's name
    createdAt: str      # ISO 8601 timestamp
    
    # DynamoDB keys
    PK: str = "USER#{userId}"
    SK: str = "PROFILE"
```

**Validation Rules**:
- `userId`: Non-empty, trimmed, 1-100 characters
- `name`: Non-empty, trimmed, 1-200 characters

### Event Model (Extended)

```python
class Event(BaseModel):
    eventId: str
    title: str
    description: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: Literal["draft", "published", "active", "cancelled", "completed"]
    waitlistEnabled: bool = False  # New field
    createdAt: str
    updatedAt: str
    
    # DynamoDB keys
    PK: str = "EVENT#{eventId}"
    SK: str = "METADATA"
```

**New Field**:
- `waitlistEnabled`: Boolean, defaults to False

### Registration Model

```python
class Registration(BaseModel):
    userId: str
    eventId: str
    status: Literal["confirmed", "waitlisted"]
    registeredAt: str    # ISO 8601 timestamp
    
    # DynamoDB keys (user-centric)
    PK: str = "USER#{userId}"
    SK: str = "EVENT#{eventId}"
```

**Additional Index Entry** (for event-centric queries):
```python
class RegistrationIndex(BaseModel):
    eventId: str
    userId: str
    status: Literal["confirmed", "waitlisted"]
    registeredAt: str
    
    # DynamoDB keys (event-centric)
    PK: str = "EVENT#{eventId}"
    SK: str = "USER#{userId}"
```

**Status Values**:
- `confirmed`: User has a confirmed spot
- `waitlisted`: User is on the waitlist

### DynamoDB Access Patterns

| Access Pattern | Key Condition | Notes |
|----------------|---------------|-------|
| Get user profile | PK = USER#{userId}, SK = PROFILE | Single item |
| Get event metadata | PK = EVENT#{eventId}, SK = METADATA | Single item |
| List user registrations | PK = USER#{userId}, SK begins_with EVENT# | Query |
| List event registrations | PK = EVENT#{eventId}, SK begins_with USER# | Query |
| Check specific registration | PK = USER#{userId}, SK = EVENT#{eventId} | Single item |


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### User Management Properties

**Property 1: User creation stores attributes correctly**

*For any* valid userId and name, when a user is created, retrieving that user should return the same userId and name.

**Validates: Requirements 1.1**

**Property 2: User uniqueness enforcement**

*For any* userId, after successfully creating a user with that userId, attempting to create another user with the same userId should be rejected.

**Validates: Requirements 1.2**

**Property 3: Whitespace validation for user fields**

*For any* string composed entirely of whitespace characters, attempting to create a user with that string as userId or name should be rejected.

**Validates: Requirements 1.3, 1.4**

### Event Capacity Properties

**Property 4: Positive capacity acceptance**

*For any* positive integer capacity value, creating or updating an event with that capacity should succeed.

**Validates: Requirements 2.1**

**Property 5: Waitlist configuration acceptance**

*For any* event, the system should accept waitlistEnabled values of true, false, or absent (defaulting to false).

**Validates: Requirements 2.2**

### Registration Properties

**Property 6: Registration with available capacity**

*For any* user and event with available capacity (confirmed registrations < capacity), registering the user should create a registration with status "confirmed".

**Validates: Requirements 3.1**

**Property 7: Duplicate registration prevention**

*For any* user and event, after successfully registering the user for the event, attempting to register the same user for the same event again should be rejected.

**Validates: Requirements 3.2**

**Property 8: Waitlist placement when at capacity**

*For any* event at full capacity (confirmed registrations = capacity) with waitlistEnabled = true, registering a new user should create a registration with status "waitlisted".

**Validates: Requirements 2.3, 3.3**

**Property 9: Rejection when at capacity without waitlist**

*For any* event at full capacity (confirmed registrations = capacity) with waitlistEnabled = false or not specified, attempting to register a new user should be rejected.

**Validates: Requirements 2.4, 3.4**

**Property 10: Non-existent event rejection**

*For any* non-existent eventId, attempting to register a user for that event should be rejected.

**Validates: Requirements 3.5**

### Unregistration Properties

**Property 11: Unregistration removes record**

*For any* registered user and event, unregistering the user should result in no registration record existing for that user-event pair.

**Validates: Requirements 4.1**

**Property 12: Waitlist promotion on unregistration**

*For any* event with at least one confirmed registration and at least one waitlisted registration, when a confirmed user unregisters, the first waitlisted user (by registeredAt timestamp) should be promoted to confirmed status.

**Validates: Requirements 4.2**

**Property 13: Invalid unregistration rejection**

*For any* user and event where the user is not registered, attempting to unregister should be rejected.

**Validates: Requirements 4.3**

### Query Properties

**Property 14: User registrations query completeness**

*For any* user with N registrations, querying that user's registered events should return exactly N events with their corresponding registration statuses.

**Validates: Requirements 5.1, 5.2**

### Data Model Properties

**Property 15: Composite key consistency**

*For any* entity stored in DynamoDB, the entity should have both a "PK" field and an "SK" field.

**Validates: Requirements 6.1**

**Property 16: User key format**

*For any* user entity, the PK should match the format "USER#{userId}" and the SK should equal "PROFILE".

**Validates: Requirements 6.2**

**Property 17: Event key format**

*For any* event entity, the PK should match the format "EVENT#{eventId}" and the SK should equal "METADATA".

**Validates: Requirements 6.3**

**Property 18: Registration key format**

*For any* registration entity, the PK should match the format "USER#{userId}" and the SK should match the format "EVENT#{eventId}".

**Validates: Requirements 6.4**

**Property 19: Event migration preserves data**

*For any* event in the old schema (with eventId as partition key), after migration to composite key schema, all event attributes should be preserved and the event should be queryable using the new key format.

**Validates: Requirements 6.6**

### Capacity Calculation Properties

**Property 20: Capacity calculation excludes waitlisted**

*For any* event with M confirmed registrations and N waitlisted registrations, the calculated available capacity should equal (capacity - M), not (capacity - M - N).

**Validates: Requirements 7.2**

## Error Handling

### Error Types

1. **ValidationError** (400)
   - Empty or whitespace-only userId or name
   - Invalid capacity values
   - Malformed request data

2. **ConflictError** (409)
   - Duplicate userId on user creation
   - Duplicate registration attempt
   - Event at capacity without waitlist

3. **NotFoundError** (404)
   - User not found
   - Event not found
   - Registration not found for unregistration

4. **DatabaseError** (500)
   - DynamoDB operation failures
   - Transaction failures
   - Conditional write failures

### Error Response Format

```json
{
  "error": "ConflictError",
  "message": "User already registered for this event",
  "detail": "userId: user123, eventId: event456"
}
```

### Consistency Guarantees

- User creation uses conditional put to prevent duplicates
- Registration operations use conditional writes to enforce capacity
- Waitlist promotion uses transactions to ensure atomicity
- All operations include proper error handling and rollback

## Testing Strategy

### Unit Testing

Unit tests will cover:
- Input validation for user and registration models
- Key format generation (PK/SK patterns)
- Error response formatting
- Edge cases: empty lists, non-existent entities
- Migration logic for existing events

### Property-Based Testing

The system will use **Hypothesis** (Python property-based testing library) to implement the 20 correctness properties defined above.

**Configuration**:
- Minimum 100 iterations per property test
- Each property test tagged with format: `**Feature: user-registration, Property {number}: {property_text}**`
- Custom generators for:
  - Valid userIds and names
  - Valid eventIds
  - Capacity values (1-100,000)
  - Whitespace strings
  - ISO 8601 timestamps

**Test Organization**:
- `test_user_properties.py` - Properties 1-3
- `test_event_properties.py` - Properties 4-5
- `test_registration_properties.py` - Properties 6-10
- `test_unregistration_properties.py` - Properties 11-13
- `test_query_properties.py` - Property 14
- `test_data_model_properties.py` - Properties 15-19
- `test_capacity_properties.py` - Property 20

**Property Test Example**:
```python
from hypothesis import given, strategies as st

@given(
    user_id=st.text(min_size=1, max_size=100).filter(lambda s: s.strip()),
    name=st.text(min_size=1, max_size=200).filter(lambda s: s.strip())
)
def test_property_1_user_creation_stores_attributes(user_id, name):
    """
    Feature: user-registration, Property 1: User creation stores attributes correctly
    
    For any valid userId and name, when a user is created,
    retrieving that user should return the same userId and name.
    """
    # Create user
    created_user = create_user(user_id, name)
    
    # Retrieve user
    retrieved_user = get_user(user_id)
    
    # Verify attributes match
    assert retrieved_user.userId == user_id
    assert retrieved_user.name == name
```

### Integration Testing

Integration tests will verify:
- End-to-end registration flows
- Waitlist promotion scenarios
- Multi-user concurrent registration (best effort)
- Database migration execution

### Test Data Management

- Use DynamoDB Local or mocked tables for testing
- Clean up test data after each test
- Use unique identifiers to avoid test interference
- Seed data for migration testing

## Implementation Notes

### DynamoDB Considerations

1. **Single Table Design**: All entities (users, events, registrations) stored in one table
2. **Composite Keys**: Enable flexible query patterns without additional GSIs
3. **Conditional Writes**: Prevent race conditions in registration operations
4. **Transactions**: Ensure atomic waitlist promotion
5. **Query Efficiency**: User registrations retrieved with single query using PK

### Migration Strategy

Existing events must be migrated to the composite key schema:

1. Scan existing events (PK = eventId, no SK)
2. For each event:
   - Create new item with PK = "EVENT#{eventId}", SK = "METADATA"
   - Copy all attributes
   - Verify new item exists
   - Delete old item
3. Update application code to use new key format
4. Deploy changes

### API Design Principles

- RESTful endpoints following existing patterns
- Consistent error responses
- Idempotent operations where possible
- Clear validation messages
- Pagination support for list operations

### Performance Considerations

- Registration operations: O(1) for capacity check with counter attribute
- User registrations query: O(N) where N = number of registrations
- Event registrations query: O(M) where M = number of registrations
- Waitlist promotion: O(N) where N = number of waitlisted users (requires scan to find first)

### Security Considerations

- Input validation on all user-provided data
- No authentication in this prototype (add for production)
- CORS configuration maintained from existing setup
- CloudWatch logging for audit trail
