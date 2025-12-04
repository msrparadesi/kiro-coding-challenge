#!/bin/bash

# Test script for Events API
# Usage: ./test-api.sh <API_URL>

set -e

if [ -z "$1" ]; then
    echo "Usage: ./test-api.sh <API_URL>"
    echo "Example: ./test-api.sh https://abc123.execute-api.us-east-1.amazonaws.com/prod"
    exit 1
fi

API_URL=$1
echo "🧪 Testing Events API at: $API_URL"
echo "========================================"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing health check..."
HEALTH=$(curl -s "$API_URL/health")
echo "Response: $HEALTH"
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Create Event
echo "2️⃣  Creating a test event..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event",
    "description": "This is a test event created by the test script",
    "date": "2024-12-15T10:00:00Z",
    "location": "Virtual",
    "capacity": 100,
    "organizer": "Test Script",
    "status": "published"
  }')

EVENT_ID=$(echo "$CREATE_RESPONSE" | grep -o '"eventId":"[^"]*"' | cut -d'"' -f4)

if [ -z "$EVENT_ID" ]; then
    echo "❌ Failed to create event"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi

echo "✅ Event created with ID: $EVENT_ID"
echo ""

# Test 3: Get Event
echo "3️⃣  Retrieving the event..."
GET_RESPONSE=$(curl -s "$API_URL/events/$EVENT_ID")
if echo "$GET_RESPONSE" | grep -q "$EVENT_ID"; then
    echo "✅ Event retrieved successfully"
else
    echo "❌ Failed to retrieve event"
    exit 1
fi
echo ""

# Test 4: List Events
echo "4️⃣  Listing all events..."
LIST_RESPONSE=$(curl -s "$API_URL/events")
if echo "$LIST_RESPONSE" | grep -q "$EVENT_ID"; then
    echo "✅ Event found in list"
else
    echo "❌ Event not found in list"
    exit 1
fi
echo ""

# Test 5: Update Event
echo "5️⃣  Updating the event..."
UPDATE_RESPONSE=$(curl -s -X PUT "$API_URL/events/$EVENT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }')
if echo "$UPDATE_RESPONSE" | grep -q "completed"; then
    echo "✅ Event updated successfully"
else
    echo "❌ Failed to update event"
    exit 1
fi
echo ""

# Test 6: Delete Event
echo "6️⃣  Deleting the event..."
DELETE_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "$API_URL/events/$EVENT_ID")
if [ "$DELETE_RESPONSE" = "204" ]; then
    echo "✅ Event deleted successfully"
else
    echo "❌ Failed to delete event (HTTP $DELETE_RESPONSE)"
    exit 1
fi
echo ""

# Test 7: Verify Deletion
echo "7️⃣  Verifying deletion..."
VERIFY_RESPONSE=$(curl -s -w "%{http_code}" "$API_URL/events/$EVENT_ID" -o /dev/null)
if [ "$VERIFY_RESPONSE" = "404" ]; then
    echo "✅ Event confirmed deleted"
else
    echo "❌ Event still exists (HTTP $VERIFY_RESPONSE)"
    exit 1
fi
echo ""

echo "========================================"
echo "🎉 All tests passed!"
echo ""
echo "Your API is working correctly. Try it out:"
echo "  - API Docs: $API_URL/docs"
echo "  - Health: $API_URL/health"
echo "  - Events: $API_URL/events"
