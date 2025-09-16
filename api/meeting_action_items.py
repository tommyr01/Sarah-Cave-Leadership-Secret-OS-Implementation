"""
Meeting Action Items Automation
Processes meeting records and creates individual action items from the Action Items field
"""

import json
import os
import re
from http.server import BaseHTTPRequestHandler
import requests
from datetime import datetime, timedelta
import calendar


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle webhook from Airtable when Meeting records are created/updated"""
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            webhook_data = json.loads(post_data.decode('utf-8'))

            # Process the webhook
            result = self.process_meeting_webhook(webhook_data)

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e), "status": "failed"}
            self.wfile.write(json.dumps(error_response).encode())

    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"status": "healthy", "service": "meeting-action-items"}
        self.wfile.write(json.dumps(response).encode())

    def process_meeting_webhook(self, webhook_data):
        """Process meeting webhook and create action items"""
        try:
            # Get environment variables
            airtable_key = os.environ.get('AIRTABLE_API_KEY')
            base_id = os.environ.get('AIRTABLE_BASE_ID')

            if not airtable_key or not base_id:
                raise Exception("Missing Airtable API credentials")

            results = []

            # Process each record in the webhook
            for record_data in webhook_data.get('records', []):
                record_id = record_data.get('id')
                fields = record_data.get('fields', {})

                # Skip if no action items
                action_items_text = fields.get('Action Items', '').strip()
                if not action_items_text:
                    continue

                # Get meeting details
                meeting_title = fields.get('Meeting Title', 'Untitled Meeting')
                attendees = fields.get('Attendees', [])
                meeting_date = fields.get('Created')

                # Get attendee names
                attendee_names = self.get_attendee_names(attendees, airtable_key, base_id)

                # Parse action items
                parsed_items = self.parse_action_items(action_items_text)

                # Create action item records with date parsing
                created_items = self.create_action_item_records(
                    parsed_items, attendee_names, meeting_title, meeting_date,
                    airtable_key, base_id
                )

                results.append({
                    "meeting_id": record_id,
                    "meeting_title": meeting_title,
                    "items_created": len(created_items),
                    "action_items": created_items
                })

            return {
                "status": "success",
                "processed_meetings": len(results),
                "results": results
            }

        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")

    def parse_action_items(self, action_items_text):
        """Parse action items from text, handling various formats"""
        items = []

        # First try to split on bullet points
        bullet_patterns = [r'•\s*', r'-\s*', r'\*\s*', r'◦\s*', r'▪\s*']

        for pattern in bullet_patterns:
            potential_items = re.split(pattern, action_items_text)
            if len(potential_items) > 1:
                # Found bullet points, use this split
                items = [item.strip() for item in potential_items if item.strip()]
                break

        # If no bullets found, split on line breaks
        if not items:
            items = [item.strip() for item in action_items_text.split('\n') if item.strip()]

        # If still no items and we have text, treat the whole text as one action item
        if not items and action_items_text.strip():
            items = [action_items_text.strip()]

        # Clean up items (remove numbering, extra whitespace)
        cleaned_items = []
        for item in items:
            # Remove leading numbers (1., 2), etc.)
            cleaned_item = re.sub(r'^\d+[\.\)]\s*', '', item)
            if cleaned_item:
                cleaned_items.append(cleaned_item)

        return cleaned_items

    def extract_due_date(self, action_item_text, reference_date=None):
        """Extract due date from action item text"""
        if not reference_date:
            reference_date = datetime.now()
        elif isinstance(reference_date, str):
            try:
                reference_date = datetime.fromisoformat(reference_date.replace('Z', '+00:00'))
            except:
                reference_date = datetime.now()

        text_lower = action_item_text.lower()

        # Pattern matching for various date formats
        date_patterns = [
            # Specific dates
            (r'(\d{4}-\d{2}-\d{2})', self.parse_iso_date),
            (r'(\d{1,2}/\d{1,2}/\d{4})', self.parse_slash_date),
            (r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s*(\d{4}))?', self.parse_month_date),

            # Relative dates
            (r'tomorrow', lambda x, ref: ref + timedelta(days=1)),
            (r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', self.parse_next_weekday),
            (r'this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', self.parse_this_weekday),
            (r'in\s+(\d+)\s+(day|days|week|weeks)', self.parse_relative_days),
            (r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', self.parse_by_weekday),
            (r'by\s+(tomorrow)', lambda x, ref: ref + timedelta(days=1)),
            (r'end\s+of\s+(week|month|year)', self.parse_end_of_period),
        ]

        for pattern, parser in date_patterns:
            if isinstance(pattern, str):
                if pattern in text_lower:
                    try:
                        return parser(text_lower, reference_date)
                    except:
                        continue
            else:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        return parser(match, reference_date)
                    except:
                        continue

        return None

    def parse_iso_date(self, match, reference_date):
        """Parse ISO format date (YYYY-MM-DD)"""
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y-%m-%d')

    def parse_slash_date(self, match, reference_date):
        """Parse slash format date (M/D/YYYY)"""
        date_str = match.group(1)
        return datetime.strptime(date_str, '%m/%d/%Y')

    def parse_month_date(self, match, reference_date):
        """Parse month name date (January 15, 2024)"""
        month_str = match.group(1)
        day_str = match.group(2)
        year_str = match.group(3) if match.group(3) else str(reference_date.year)

        month_num = list(calendar.month_name).index(month_str.capitalize())
        return datetime(int(year_str), month_num, int(day_str))

    def parse_next_weekday(self, match, reference_date):
        """Parse 'next Monday' style dates"""
        weekday_str = match.group(1)
        weekday_num = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].index(weekday_str)

        days_ahead = weekday_num - reference_date.weekday()
        if days_ahead <= 0:  # Target day is today or in the past, so next week
            days_ahead += 7

        return reference_date + timedelta(days=days_ahead)

    def parse_this_weekday(self, match, reference_date):
        """Parse 'this Friday' style dates"""
        weekday_str = match.group(1)
        weekday_num = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].index(weekday_str)

        days_ahead = weekday_num - reference_date.weekday()
        if days_ahead < 0:  # Target day is in the past, so next week
            days_ahead += 7

        return reference_date + timedelta(days=days_ahead)

    def parse_by_weekday(self, match, reference_date):
        """Parse 'by Friday' style dates"""
        return self.parse_this_weekday(match, reference_date)

    def parse_relative_days(self, match, reference_date):
        """Parse 'in 2 weeks' or 'in 3 days' style dates"""
        number = int(match.group(1))
        period = match.group(2)

        if period.startswith('day'):
            return reference_date + timedelta(days=number)
        elif period.startswith('week'):
            return reference_date + timedelta(weeks=number)

        return None

    def parse_end_of_period(self, match, reference_date):
        """Parse 'end of week/month/year' style dates"""
        period = match.group(1)

        if period == 'week':
            # End of current week (Sunday)
            days_until_sunday = (6 - reference_date.weekday()) % 7
            return reference_date + timedelta(days=days_until_sunday)
        elif period == 'month':
            # Last day of current month
            next_month = reference_date.replace(day=28) + timedelta(days=4)
            return next_month - timedelta(days=next_month.day)
        elif period == 'year':
            # December 31 of current year
            return reference_date.replace(month=12, day=31)

        return None

    def get_attendee_names(self, attendee_record_ids, airtable_key, base_id):
        """Get attendee names from their record IDs"""
        if not attendee_record_ids:
            return []

        try:
            # Get attendee records from Clients table
            headers = {
                'Authorization': f'Bearer {airtable_key}',
                'Content-Type': 'application/json'
            }

            names = []
            for record_id in attendee_record_ids:
                url = f'https://api.airtable.com/v0/{base_id}/Clients/{record_id}'
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    record_data = response.json()
                    client_name = record_data.get('fields', {}).get('Client Name', 'Unknown')
                    names.append(client_name)
                else:
                    names.append('Unknown Attendee')

            return names

        except Exception as e:
            print(f"Error getting attendee names: {e}")
            return ['Unknown Attendee'] * len(attendee_record_ids)

    def create_action_item_records(self, parsed_items, attendee_names, meeting_title, meeting_date, airtable_key, base_id):
        """Create individual action item records in the Action Items table"""
        if not parsed_items:
            return []

        try:
            headers = {
                'Authorization': f'Bearer {airtable_key}',
                'Content-Type': 'application/json'
            }

            # Format attendee names for inclusion
            attendee_prefix = ""
            if attendee_names:
                attendee_prefix = f"{', '.join(attendee_names)}: "

            # Prepare records for bulk creation
            records_to_create = []
            for item in parsed_items:
                action_item_text = f"{attendee_prefix}{item}"

                # Extract due date if present
                due_date = self.extract_due_date(item, meeting_date)

                # Build record fields
                record_fields = {
                    "Action Item": action_item_text,
                    "Status": "Not Started",
                    "Priority": "Medium"
                }

                # Add due date only if found
                if due_date:
                    record_fields["Due Date"] = due_date.strftime('%Y-%m-%d')

                record = {"fields": record_fields}
                records_to_create.append(record)

            # Create records in Airtable (max 10 per request)
            created_items = []
            for i in range(0, len(records_to_create), 10):
                batch = records_to_create[i:i+10]

                url = f'https://api.airtable.com/v0/{base_id}/Action%20Items'
                payload = {"records": batch}

                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    batch_results = response.json().get('records', [])
                    for record in batch_results:
                        created_items.append({
                            "id": record.get('id'),
                            "action_item": record.get('fields', {}).get('Action Item'),
                            "due_date": record.get('fields', {}).get('Due Date'),
                            "status": record.get('fields', {}).get('Status')
                        })
                else:
                    print(f"Failed to create action items batch: {response.text}")

            return created_items

        except Exception as e:
            print(f"Error creating action item records: {e}")
            return []