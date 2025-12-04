# Implementation Plan

- [ ] 1. Update DynamoDB infrastructure to support composite key schema
- [ ] 1.1 Modify CDK stack to update table schema with PK and SK as keys
  - Update infrastructure/lib/infrastructure-stack.ts
  - Change partition key from 'eventId' to 'PK'
  - Add sort key 'SK'
  - Remove or update existing GSI to work with new schema
  - _Requirements: 6.1_

- [ ] 1.2 Add environment variables for table configuration
  - Ensure Lambda has access to table name
  - _Requirements: 6.1_

- [ ] 2. Implement composite key data models
- [ ] 2.1 Create User model with composite key support
  - Add User, UserCreate models to backend/app/models.py
  - Include PK/SK generation logic
  - Add validation for userId and name (whitespace, length)
  - _Requirements: 1.1, 1.3, 1.4, 6.2_

- [ ] 2.2 Extend Event model with waitlist support
  - Add waitlistEnabled field to Event models
  - Update EventCreate and EventUpdate models
  - Modify Event model to include PK/SK fields
  - _Requirements: 2.2, 6.3_

- [ ] 2.3 Create Registration model with composite key support
  - Add Registration, RegistrationCreate models
  - Include status field (confirmed/waitlisted)
  - Add PK/SK generation for both user-centric and event-centric access
  - _Requirements: 3.1, 3.3, 6.4_

- [ ] 3. Update database layer for composite key operations
- [ ] 3.1 Modify database.py to support composite key operations
  - Update put_item, get_item, delete_item for PK/SK
  - Add query operation for composite key patterns
  - Add conditional_put for uniqueness constraints
  - Add transaction support for atomic operations
  - _Requirements: 6.1, 6.5_

- [ ] 3.2 Implement event migration utility
  - Create function to migrate existing events to composite key schema
  - Scan old format events (PK=eventId)
  - Transform to new format (PK=EVENT#{eventId}, SK=METADATA)
  - Preserve all event attributes
  - _Requirements: 6.6_

- [ ]* 3.3 Write property test for event migration
  - **Property 19: Event migration preserves data**
  - **Validates: Requirements 6.6**

- [ ] 4. Implement User service and endpoints
- [ ] 4.1 Create user service functions
  - Implement create_user with uniqueness check
  - Implement get_user
  - Implement get_user_registrations
  - _Requirements: 1.1, 1.2, 5.1_

- [ ]* 4.2 Write property tests for user operations
  - **Property 1: User creation stores attributes correctly**
  - **Validates: Requirements 1.1**

- [ ]* 4.3 Write property test for user uniqueness
  - **Property 2: User uniqueness enforcement**
  - **Validates: Requirements 1.2**

- [ ]* 4.4 Write property test for whitespace validation
  - **Property 3: Whitespace validation for user fields**
  - **Validates: Requirements 1.3, 1.4**

- [ ] 4.5 Add user API endpoints to main.py
  - POST /users - Create user
  - GET /users/{userId} - Get user profile
  - GET /users/{userId}/registrations - List user registrations
  - _Requirements: 1.1, 5.1_

- [ ] 5. Implement Registration service and endpoints
- [ ] 5.1 Create registration service functions
  - Implement register_user_for_event with capacity checking
  - Implement unregister_user_from_event with waitlist promotion
  - Implement get_event_registrations
  - Implement count_confirmed_registrations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 7.2_

- [ ]* 5.2 Write property test for registration with available capacity
  - **Property 6: Registration with available capacity**
  - **Validates: Requirements 3.1**

- [ ]* 5.3 Write property test for duplicate registration prevention
  - **Property 7: Duplicate registration prevention**
  - **Validates: Requirements 3.2**

- [ ]* 5.4 Write property test for waitlist placement
  - **Property 8: Waitlist placement when at capacity**
  - **Validates: Requirements 2.3, 3.3**

- [ ]* 5.5 Write property test for rejection without waitlist
  - **Property 9: Rejection when at capacity without waitlist**
  - **Validates: Requirements 2.4, 3.4**

- [ ]* 5.6 Write property test for non-existent event rejection
  - **Property 10: Non-existent event rejection**
  - **Validates: Requirements 3.5**

- [ ] 5.7 Add registration API endpoints to main.py
  - POST /events/{eventId}/register - Register user (accepts userId in body)
  - DELETE /events/{eventId}/register/{userId} - Unregister user
  - GET /events/{eventId}/registrations - List event registrations
  - _Requirements: 3.1, 4.1_

- [ ] 6. Implement unregistration with waitlist promotion
- [ ] 6.1 Create waitlist promotion logic
  - Query waitlisted users ordered by registeredAt
  - Promote first waitlisted user to confirmed
  - Use transaction for atomicity
  - _Requirements: 4.2_

- [ ]* 6.2 Write property test for unregistration removes record
  - **Property 11: Unregistration removes record**
  - **Validates: Requirements 4.1**

- [ ]* 6.3 Write property test for waitlist promotion
  - **Property 12: Waitlist promotion on unregistration**
  - **Validates: Requirements 4.2**

- [ ]* 6.4 Write property test for invalid unregistration rejection
  - **Property 13: Invalid unregistration rejection**
  - **Validates: Requirements 4.3**

- [ ] 7. Implement query operations and property tests
- [ ] 7.1 Implement user registrations query with event details
  - Query registrations by user PK
  - Fetch event details for each registration
  - Include registration status
  - _Requirements: 5.1, 5.2_

- [ ]* 7.2 Write property test for user registrations query
  - **Property 14: User registrations query completeness**
  - **Validates: Requirements 5.1, 5.2**

- [ ] 8. Add property tests for event capacity
- [ ]* 8.1 Write property test for positive capacity acceptance
  - **Property 4: Positive capacity acceptance**
  - **Validates: Requirements 2.1**

- [ ]* 8.2 Write property test for waitlist configuration
  - **Property 5: Waitlist configuration acceptance**
  - **Validates: Requirements 2.2**

- [ ]* 8.3 Write property test for capacity calculation
  - **Property 20: Capacity calculation excludes waitlisted**
  - **Validates: Requirements 7.2**

- [ ] 9. Add property tests for data model consistency
- [ ]* 9.1 Write property test for composite key consistency
  - **Property 15: Composite key consistency**
  - **Validates: Requirements 6.1**

- [ ]* 9.2 Write property test for user key format
  - **Property 16: User key format**
  - **Validates: Requirements 6.2**

- [ ]* 9.3 Write property test for event key format
  - **Property 17: Event key format**
  - **Validates: Requirements 6.3**

- [ ]* 9.4 Write property test for registration key format
  - **Property 18: Registration key format**
  - **Validates: Requirements 6.4**

- [ ] 10. Update existing event endpoints for composite key schema
- [ ] 10.1 Modify event CRUD operations in main.py
  - Update create_event to use composite keys
  - Update get_event to use composite keys
  - Update list_events to query with composite keys
  - Update update_event to use composite keys
  - Update delete_event to use composite keys
  - _Requirements: 6.3_

- [ ] 11. Deploy and verify
- [ ] 11.1 Run migration script for existing events
  - Execute migration utility on deployed DynamoDB table
  - Verify all events migrated successfully
  - _Requirements: 6.6_

- [ ] 11.2 Deploy infrastructure and application updates
  - Run cdk deploy to update infrastructure
  - Verify all endpoints are functional
  - Test registration flows end-to-end
  - _Requirements: All_

- [ ] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
