import boto3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from botocore.exceptions import ClientError, BotoCoreError
import logging

from .exceptions import DatabaseException, EventNotFoundException

logger = logging.getLogger(__name__)


class DynamoDBClient:
    def __init__(self):
        self.table_name = os.getenv("DYNAMODB_TABLE_NAME", "EventsTable")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        
        try:
            # Initialize DynamoDB client
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"Connected to DynamoDB table: {self.table_name} in region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
            raise DatabaseException(
                "Failed to connect to database",
                original_error=e
            )
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event in DynamoDB"""
        # Use provided eventId or generate a new UUID
        event_id = event_data.pop('eventId', None) or str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        item = {
            'eventId': event_id,
            'createdAt': timestamp,
            'updatedAt': timestamp,
            **event_data
        }
        
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(eventId)'
            )
            logger.info(f"Created event: {event_id}")
            return item
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                raise DatabaseException("Event with this ID already exists")
            logger.error(f"Error creating event: {e.response['Error']['Message']}")
            raise DatabaseException(
                f"Failed to create event: {e.response['Error']['Message']}",
                original_error=e
            )
        except BotoCoreError as e:
            logger.error(f"BotoCore error creating event: {str(e)}")
            raise DatabaseException("Database connection error", original_error=e)
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID"""
        if not event_id or not event_id.strip():
            raise DatabaseException("Event ID cannot be empty")
        
        try:
            response = self.table.get_item(
                Key={'eventId': event_id},
                ConsistentRead=True
            )
            item = response.get('Item')
            if item:
                logger.info(f"Retrieved event: {event_id}")
            return item
        except ClientError as e:
            logger.error(f"Error getting event {event_id}: {e.response['Error']['Message']}")
            raise DatabaseException(
                f"Failed to retrieve event: {e.response['Error']['Message']}",
                original_error=e
            )
        except BotoCoreError as e:
            logger.error(f"BotoCore error getting event: {str(e)}")
            raise DatabaseException("Database connection error", original_error=e)
    
    def list_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all events with optional limit"""
        try:
            scan_kwargs = {}
            if limit:
                scan_kwargs['Limit'] = limit
            
            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                if limit:
                    scan_kwargs['Limit'] = limit - len(items)
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
            
            logger.info(f"Listed {len(items)} events")
            return items
        except ClientError as e:
            logger.error(f"Error listing events: {e.response['Error']['Message']}")
            raise DatabaseException(
                f"Failed to list events: {e.response['Error']['Message']}",
                original_error=e
            )
        except BotoCoreError as e:
            logger.error(f"BotoCore error listing events: {str(e)}")
            raise DatabaseException("Database connection error", original_error=e)
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an event"""
        if not event_id or not event_id.strip():
            raise DatabaseException("Event ID cannot be empty")
        
        if not update_data:
            return self.get_event(event_id)
        
        # Build update expression
        update_expression = "SET updatedAt = :updatedAt"
        expression_values = {':updatedAt': datetime.utcnow().isoformat() + 'Z'}
        expression_names = {}
        
        for key, value in update_data.items():
            if value is not None:
                placeholder = f":{key}"
                # Handle reserved keywords
                if key in ['status', 'date', 'location']:
                    attr_name = f"#{key}"
                    expression_names[attr_name] = key
                    update_expression += f", {attr_name} = {placeholder}"
                else:
                    update_expression += f", {key} = {placeholder}"
                expression_values[placeholder] = value
        
        try:
            update_kwargs = {
                'Key': {'eventId': event_id},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values,
                'ConditionExpression': 'attribute_exists(eventId)',
                'ReturnValues': 'ALL_NEW'
            }
            
            if expression_names:
                update_kwargs['ExpressionAttributeNames'] = expression_names
            
            response = self.table.update_item(**update_kwargs)
            logger.info(f"Updated event: {event_id}")
            return response.get('Attributes')
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                raise EventNotFoundException(event_id)
            logger.error(f"Error updating event {event_id}: {e.response['Error']['Message']}")
            raise DatabaseException(
                f"Failed to update event: {e.response['Error']['Message']}",
                original_error=e
            )
        except BotoCoreError as e:
            logger.error(f"BotoCore error updating event: {str(e)}")
            raise DatabaseException("Database connection error", original_error=e)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        if not event_id or not event_id.strip():
            raise DatabaseException("Event ID cannot be empty")
        
        try:
            self.table.delete_item(
                Key={'eventId': event_id},
                ConditionExpression='attribute_exists(eventId)'
            )
            logger.info(f"Deleted event: {event_id}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ConditionalCheckFailedException':
                raise EventNotFoundException(event_id)
            logger.error(f"Error deleting event {event_id}: {e.response['Error']['Message']}")
            raise DatabaseException(
                f"Failed to delete event: {e.response['Error']['Message']}",
                original_error=e
            )
        except BotoCoreError as e:
            logger.error(f"BotoCore error deleting event: {str(e)}")
            raise DatabaseException("Database connection error", original_error=e)


# Singleton instance
db_client = DynamoDBClient()
