"""Calendar export functionality for symposium schedules."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
import icalendar
from icalendar import Calendar, Event, Todo
import pytz
from symposium.core.config import Config
from symposium.io.readers import ReportReader

logger = logging.getLogger(__name__)


class ScheduleExporter:
    """Exporter for symposium schedules to calendar formats."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize schedule exporter.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.timezone = pytz.timezone(self.config.get('timezone', 'UTC'))

    def parse_schedule_data(self, schedule_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse schedule data into structured event format.

        Args:
            schedule_data: Raw schedule data

        Returns:
            List of structured event dictionaries
        """
        events = []

        # Handle different input formats
        if isinstance(schedule_data, dict):
            if 'events' in schedule_data:
                events = schedule_data['events']
            elif 'sessions' in schedule_data:
                events = schedule_data['sessions']
            else:
                # Single event
                events = [schedule_data]

        elif isinstance(schedule_data, list):
            events = schedule_data

        # Validate and structure events
        structured_events = []
        for event in events:
            structured_event = self._structure_event(event)
            if structured_event:
                structured_events.append(structured_event)

        logger.info(f"Parsed {len(structured_events)} events from schedule data")
        return structured_events

    def _structure_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Structure individual event data.

        Args:
            event: Raw event data

        Returns:
            Structured event dictionary or None if invalid
        """
        try:
            # Required fields validation
            if not event.get('title'):
                logger.warning(f"Event missing title: {event}")
                return None

            if not event.get('start_time'):
                logger.warning(f"Event missing start_time: {event}")
                return None

            # Check if already structured (datetime objects)
            start_time = event['start_time']
            if hasattr(start_time, 'strftime'):  # Already a datetime object
                start_dt = start_time
            else:  # Need to parse string
                start_dt = self._parse_datetime(str(start_time))

            end_time = event.get('end_time')
            if hasattr(end_time, 'strftime'):  # Already a datetime object
                end_dt = end_time
            else:  # Need to parse string or calculate from duration
                if end_time:
                    end_dt = self._parse_datetime(str(end_time))
                else:
                    end_dt = start_dt + timedelta(hours=event.get('duration_hours', 1))

            # Structure the event
            structured = {
                'uid': event.get('uid', str(uuid.uuid4())),
                'title': event['title'],
                'description': event.get('description', ''),
                'start_time': start_dt,
                'end_time': end_dt,
                'location': event.get('location', ''),
                'organizer': event.get('organizer', ''),
                'speakers': event.get('speakers', []),
                'category': event.get('category', 'General'),
                'url': event.get('url', ''),
                'tags': event.get('tags', [])
            }

            return structured

        except Exception as e:
            logger.error(f"Error structuring event {event.get('title', 'Unknown')}: {e}")
            return None

    def _parse_datetime(self, time_str: str) -> datetime:
        """Parse datetime string into timezone-aware datetime.

        Args:
            time_str: Time string in various formats

        Returns:
            Timezone-aware datetime object
        """
        # Try different datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%d'
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                return self.timezone.localize(dt)
            except ValueError:
                continue

        # If no format matches, assume current time + offset
        logger.warning(f"Could not parse datetime: {time_str}")
        return datetime.now(self.timezone)

    def create_ics_calendar(
        self,
        events: List[Dict[str, Any]],
        calendar_name: str = "Symposium Schedule",
        description: str = "Active Inference Symposium Schedule"
    ) -> Calendar:
        """Create ICS calendar from structured events.

        Args:
            events: List of structured event dictionaries
            calendar_name: Name of the calendar
            description: Calendar description

        Returns:
            ICS Calendar object
        """
        cal = Calendar()
        cal.add('prodid', f'-//Symposium Calendar//{calendar_name}//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', calendar_name)
        cal.add('x-wr-timezone', str(self.timezone))

        # Add events to calendar
        for event_data in events:
            event = self._create_ics_event(event_data)
            cal.add_component(event)

        logger.info(f"Created ICS calendar '{calendar_name}' with {len(events)} events")
        return cal

    def _create_ics_event(self, event_data: Dict[str, Any]) -> Event:
        """Create ICS event from structured event data.

        Args:
            event_data: Structured event dictionary

        Returns:
            ICS Event object
        """
        event = Event()

        # Basic event properties
        event.add('uid', event_data['uid'])
        event.add('summary', event_data['title'])
        event.add('dtstart', event_data['start_time'])
        event.add('dtend', event_data['end_time'])
        event.add('dtstamp', datetime.now(self.timezone))
        event.add('created', datetime.now(self.timezone))
        event.add('last-modified', datetime.now(self.timezone))

        # Optional properties
        if event_data['description']:
            event.add('description', event_data['description'])

        if event_data['location']:
            event.add('location', event_data['location'])

        if event_data['organizer']:
            event.add('organizer', event_data['organizer'])

        if event_data['url']:
            event.add('url', event_data['url'])

        # Categories
        if event_data['category']:
            event.add('categories', event_data['category'])

        # Custom properties for symposium
        if event_data['speakers']:
            speakers_str = ', '.join(event_data['speakers'])
            event.add('x-symposium-speakers', speakers_str)

        if event_data['tags']:
            tags_str = ', '.join(event_data['tags'])
            event.add('x-symposium-tags', tags_str)

        return event

    def export_ics_file(
        self,
        events: List[Dict[str, Any]],
        output_path: Path,
        calendar_name: str = "Symposium Schedule",
        description: str = "Active Inference Symposium Schedule"
    ) -> bool:
        """Export events to ICS file.

        Args:
            events: List of structured event dictionaries
            output_path: Output file path
            calendar_name: Name of the calendar
            description: Calendar description

        Returns:
            Success status
        """
        try:
            # Create calendar
            cal = self.create_ics_calendar(events, calendar_name, description)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to ICS format (this is where errors might occur)
            ics_content = cal.to_ical()

            # Write to file
            with open(output_path, 'wb') as f:
                f.write(ics_content)

            logger.info(f"ICS calendar exported to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting ICS file: {e}")
            # Clean up partial file if it exists
            if output_path.exists():
                output_path.unlink()
            return False

    def export_symposium_schedule(
        self,
        schedule_data: Dict[str, Any],
        output_path: Path,
        calendar_name: str = "Active Inference Symposium",
        description: str = "Active Inference Symposium Schedule"
    ) -> bool:
        """Export complete symposium schedule to ICS format.

        Args:
            schedule_data: Symposium schedule data
            output_path: Output file path
            calendar_name: Calendar name
            description: Calendar description

        Returns:
            Success status
        """
        try:
            # Parse schedule data
            events = self.parse_schedule_data(schedule_data)

            if not events:
                logger.error("No valid events found in schedule data")
                return False

            # Export to ICS
            success = self.export_ics_file(events, output_path, calendar_name, description)

            if success:
                logger.info(f"Successfully exported symposium schedule with {len(events)} events")

            return success

        except Exception as e:
            logger.error(f"Error exporting symposium schedule: {e}")
            return False

    def export_from_csv(
        self,
        csv_path: Path,
        output_path: Path,
        calendar_name: str = "Symposium Schedule",
        **kwargs
    ) -> bool:
        """Export schedule from CSV file to ICS format.

        Args:
            csv_path: Path to CSV file with schedule data
            output_path: Output ICS file path
            calendar_name: Calendar name
            **kwargs: Additional configuration

        Returns:
            Success status
        """
        try:
            # Load CSV data
            import pandas as pd
            df = pd.read_csv(csv_path)

            # Convert to schedule format and structure events
            events = []
            for _, row in df.iterrows():
                event = {
                    'title': row.get('title', row.get('session', 'Untitled')),
                    'start_time': row.get('start_time', row.get('datetime', '')),
                    'description': row.get('description', row.get('abstract', '')),
                    'location': row.get('location', row.get('venue', '')),
                    'speakers': [s.strip() for s in str(row.get('speakers', '')).split(',') if s.strip()],
                    'category': row.get('category', row.get('type', 'General')),
                    'duration_hours': row.get('duration_hours', 1)
                }
                events.append(event)

            # Structure events properly
            structured_events = []
            for event in events:
                structured = self._structure_event(event)
                if structured:
                    structured_events.append(structured)

            if not structured_events:
                logger.error("No valid events found in CSV data")
                return False

            # Export to ICS
            return self.export_ics_file(structured_events, output_path, calendar_name, **kwargs)

        except Exception as e:
            logger.error(f"Error exporting from CSV: {e}")
            return False

    def validate_schedule(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate schedule data and detect issues.

        Args:
            events: List of structured event dictionaries

        Returns:
            Validation report dictionary
        """
        report = {
            'total_events': len(events),
            'valid_events': 0,
            'warnings': [],
            'errors': [],
            'conflicts': []
        }

        event_times = []

        for event in events:
            # Check required fields
            if not event.get('title'):
                report['errors'].append(f"Event missing title: {event}")
                continue

            if not event.get('start_time'):
                report['errors'].append(f"Event missing start_time: {event['title']}")
                continue

            # Structure event to get datetime objects
            structured_event = self._structure_event(event)
            if not structured_event:
                report['errors'].append(f"Event could not be structured: {event['title']}")
                continue

            # Check for conflicts
            event_start = structured_event['start_time']
            event_end = structured_event['end_time']

            for existing_start, existing_end in event_times:
                if (event_start < existing_end and event_end > existing_start):
                    report['conflicts'].append({
                        'event1': f"{existing_start} - {existing_end}",
                        'event2': f"{event['title']} ({event_start} - {event_end})"
                    })
                    break

            event_times.append((event_start, event_end))
            report['valid_events'] += 1

        logger.info(f"Schedule validation: {report['valid_events']}/{report['total_events']} valid events")
        return report
