# Calendar Module

Calendar and schedule export functionality for the Symposium package.

## Overview

This module provides comprehensive calendar export capabilities for symposium schedules, including ICS (iCalendar) format support for integration with calendar applications.

## Components

### ScheduleExporter
Calendar export utilities for symposium schedules:
- ICS format calendar generation
- Event scheduling and organization
- Multi-format calendar export
- Timezone and recurrence support

## Usage

```python
from symposium.calendar import ScheduleExporter

# Create schedule exporter
exporter = ScheduleExporter(config)

# Export symposium schedule to ICS
exporter.export_symposium_schedule(
    schedule_data, output_path, calendar_name="Active Inference Symposium 2025"
)
```

### Timestamp and publication guarantees

`ScheduleExporter` accepts ISO datetime strings and `datetime` objects. `Z` and
explicit offsets preserve their instant; naive values use the configured timezone.
Invalid supplied timestamps raise `ValueError` instead of becoming the current time.

Calendar serialization completes before publication. The exporter writes, flushes,
syncs and closes its own same-directory temporary file before atomic replacement.
A failed publication preserves an existing destination and cleans only that
operation's temporary file.

This legacy exporter is separate from approved-public calendar generation. These
guarantees do not regenerate or requalify released calendars or books.

## Export Formats

### ICS (iCalendar)
- Standard calendar format compatible with most calendar applications
- Event details including title, description, location, time
- Recurring events and exceptions
- Attendee and organizer information

## Data Requirements

### Schedule Data
- Event titles and descriptions
- Start and end times
- Location information
- Speaker/presenter details
- Session types and categories

### Configuration
- Timezone settings
- Calendar metadata
- Export preferences
- File naming conventions

## Integration

This module integrates with:
- `symposium.core` - Configuration and logging
- `symposium.io` - File writing operations
- External calendar applications - ICS format compatibility

## Features

- **Multi-timezone Support**: Handle events across different timezones
- **Recurring Events**: Support for repeated sessions and workshops
- **Rich Event Data**: Include abstracts, speaker bios, and session materials
- **Validation**: Ensure calendar data integrity and format compliance
- **Error Handling**: Graceful handling of missing or invalid data









