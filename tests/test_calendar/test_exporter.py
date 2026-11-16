"""Tests for calendar export functionality."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import icalendar
import pytest

import symposium.calendar.exporter as exporter_module
from symposium.calendar.exporter import ScheduleExporter


class TestScheduleExporter:
    """Tests for ScheduleExporter class."""

    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return {
            "title": "Keynote: Active Inference Overview",
            "start_time": "2025-06-15 09:00:00",
            "description": "Opening keynote on active inference principles",
            "location": "Main Auditorium",
            "organizer": "Dr. Karl Friston",
            "speakers": ["Karl Friston"],
            "category": "Keynote",
            "url": "https://symposium.ai/session/1",
            "tags": ["keynote", "active-inference"],
        }

    @pytest.fixture
    def sample_schedule_data(self):
        """Sample schedule data for testing."""
        return {
            "events": [
                {
                    "title": "Registration",
                    "start_time": "2025-06-15 08:00:00",
                    "description": "Registration and welcome coffee",
                    "location": "Registration Desk",
                    "category": "Registration",
                },
                {
                    "title": "Keynote: Active Inference Overview",
                    "start_time": "2025-06-15 09:00:00",
                    "description": "Opening keynote on active inference principles",
                    "location": "Main Auditorium",
                    "speakers": ["Karl Friston"],
                    "category": "Keynote",
                },
                {
                    "title": "Coffee Break",
                    "start_time": "2025-06-15 10:30:00",
                    "description": "Morning coffee break",
                    "location": "Exhibition Hall",
                    "category": "Break",
                },
            ]
        }

    @pytest.fixture
    def exporter(self):
        """ScheduleExporter instance for testing."""
        return ScheduleExporter({"timezone": "UTC"})

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        exporter = ScheduleExporter()
        assert exporter.config == {}
        assert exporter.timezone.zone == "UTC"

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = {"timezone": "America/New_York"}
        exporter = ScheduleExporter(config)
        assert exporter.config == config
        assert "America/New_York" in str(exporter.timezone)

    def test_structure_event_valid(self, sample_event_data):
        """Test structuring valid event data."""
        exporter = ScheduleExporter()
        result = exporter._structure_event(sample_event_data)

        assert result is not None
        assert result["title"] == sample_event_data["title"]
        assert result["description"] == sample_event_data["description"]
        assert result["location"] == sample_event_data["location"]
        assert result["category"] == sample_event_data["category"]
        assert "uid" in result
        assert "start_time" in result
        assert "end_time" in result

    def test_structure_event_missing_title(self):
        """Test structuring event with missing title."""
        exporter = ScheduleExporter()
        event_data = {"start_time": "2025-06-15 09:00:00"}

        result = exporter._structure_event(event_data)
        assert result is None

    def test_structure_event_missing_start_time(self):
        """Test structuring event with missing start_time."""
        exporter = ScheduleExporter()
        event_data = {"title": "Test Event"}

        result = exporter._structure_event(event_data)
        assert result is None

    def test_parse_datetime_various_formats(self):
        """Test parsing datetime in various formats."""
        exporter = ScheduleExporter()

        # Test different formats
        formats = [
            "2025-06-15 09:00:00",
            "2025-06-15T09:00:00",
            "2025-06-15 09:00",
            "2025-06-15T09:00",
        ]

        for time_str in formats:
            result = exporter._parse_datetime(time_str)
            assert result is not None
            assert result.year == 2025
            assert result.month == 6
            assert result.day == 15

    @pytest.mark.parametrize(
        "value", ["invalid_datetime", "2025-02-30T09:00:00", "2025-06-15T09:00:00+25:00", ""]
    )
    def test_parse_datetime_invalid(self, value):
        exporter = ScheduleExporter()
        with pytest.raises(ValueError):
            exporter._parse_datetime(value)

    def test_parse_schedule_data_dict_format(self, sample_schedule_data):
        """Test parsing schedule data in dictionary format."""
        exporter = ScheduleExporter()
        events = exporter.parse_schedule_data(sample_schedule_data)

        assert len(events) == 3
        assert events[0]["title"] == "Registration"
        assert events[1]["title"] == "Keynote: Active Inference Overview"

    def test_parse_schedule_data_list_format(self):
        """Test parsing schedule data in list format."""
        schedule_data = [
            {"title": "Event 1", "start_time": "2025-06-15 09:00:00"},
            {"title": "Event 2", "start_time": "2025-06-15 10:00:00"},
        ]

        exporter = ScheduleExporter()
        events = exporter.parse_schedule_data(schedule_data)

        assert len(events) == 2
        assert events[0]["title"] == "Event 1"
        assert events[1]["title"] == "Event 2"

    def test_parse_schedule_data_single_event(self):
        """Test parsing single event data."""
        schedule_data = {"title": "Single Event", "start_time": "2025-06-15 09:00:00"}

        exporter = ScheduleExporter()
        events = exporter.parse_schedule_data(schedule_data)

        assert len(events) == 1
        assert events[0]["title"] == "Single Event"

    def test_create_ics_calendar(self, sample_schedule_data, exporter):
        """Test creating ICS calendar from events."""
        events = exporter.parse_schedule_data(sample_schedule_data)
        calendar_name = "Test Symposium"
        description = "Test calendar description"

        cal = exporter.create_ics_calendar(events, calendar_name, description)

        assert isinstance(cal, icalendar.Calendar)
        assert cal["prodid"] == f"-//Symposium Calendar//{calendar_name}//EN"
        assert cal["x-wr-calname"] == calendar_name

        # Check that events were added
        components = cal.subcomponents
        assert len([c for c in components if isinstance(c, icalendar.Event)]) == 3

    def test_create_ics_event(self, sample_event_data, exporter):
        """Test creating individual ICS event."""
        structured_event = exporter._structure_event(sample_event_data)
        event = exporter._create_ics_event(structured_event)

        assert isinstance(event, icalendar.Event)
        assert event["summary"] == sample_event_data["title"]
        assert event["description"] == sample_event_data["description"]
        assert event["location"] == sample_event_data["location"]
        assert event["uid"] == structured_event["uid"]

    def test_export_ics_file(self, sample_schedule_data, exporter, tmp_path):
        """Test exporting events to ICS file."""
        events = exporter.parse_schedule_data(sample_schedule_data)
        output_path = tmp_path / "test_schedule.ics"

        success = exporter.export_ics_file(events, output_path, "Test Calendar")

        assert success
        assert output_path.exists()

        # Verify file content
        with open(output_path, "rb") as f:
            content = f.read()

        cal = icalendar.Calendar.from_ical(content)
        assert cal["x-wr-calname"] == "Test Calendar"

    def test_export_symposium_schedule(self, sample_schedule_data, exporter, tmp_path):
        """Test exporting complete symposium schedule."""
        output_path = tmp_path / "symposium_schedule.ics"

        success = exporter.export_symposium_schedule(
            sample_schedule_data, output_path, "Active Inference Symposium 2025"
        )

        assert success
        assert output_path.exists()

        # Verify calendar content
        with open(output_path, "rb") as f:
            content = f.read()

        cal = icalendar.Calendar.from_ical(content)
        assert cal["x-wr-calname"] == "Active Inference Symposium 2025"

    def test_export_from_csv(self, exporter, tmp_path):
        """Test exporting schedule from CSV file."""
        # Create test CSV file
        csv_path = tmp_path / "schedule.csv"
        csv_content = """title,start_time,description,location,category
Event 1,2025-06-15 09:00:00,First event,Room A,Session
Event 2,2025-06-15 10:00:00,Second event,Room B,Session
"""

        with open(csv_path, "w") as f:
            f.write(csv_content)

        output_path = tmp_path / "from_csv.ics"
        success = exporter.export_from_csv(csv_path, output_path, "CSV Calendar")

        assert success
        assert output_path.exists()

    def test_validate_schedule_valid(self, sample_schedule_data, exporter):
        """Test validating valid schedule."""
        events = exporter.parse_schedule_data(sample_schedule_data)
        report = exporter.validate_schedule(events)

        assert report["total_events"] == 3
        assert report["valid_events"] == 3
        assert len(report["errors"]) == 0
        assert len(report["conflicts"]) == 0

    def test_validate_schedule_with_conflicts(self, exporter):
        """Test validating schedule with time conflicts."""
        conflicting_events = [
            {
                "title": "Event 1",
                "start_time": "2025-06-15 09:00:00",
                "end_time": "2025-06-15 10:00:00",
            },
            {
                "title": "Event 2",
                "start_time": "2025-06-15 09:30:00",  # Overlaps with Event 1
                "end_time": "2025-06-15 10:30:00",
            },
        ]

        report = exporter.validate_schedule(conflicting_events)

        assert report["total_events"] == 2
        assert report["valid_events"] == 2
        assert len(report["conflicts"]) == 1

    def test_validate_schedule_invalid_events(self, exporter):
        """Test validating schedule with invalid events."""
        invalid_events = [
            {"title": "Valid Event", "start_time": "2025-06-15 09:00:00"},
            {"title": "", "start_time": "2025-06-15 10:00:00"},  # Missing title
            {"title": "No Start Time"},  # Missing start_time
        ]

        report = exporter.validate_schedule(invalid_events)

        assert report["total_events"] == 3
        assert report["valid_events"] == 1  # Only first event is valid
        assert len(report["errors"]) == 2

    def test_export_ics_file_with_error(self, exporter, tmp_path):
        """Test handling errors during ICS export."""
        # Test with invalid event data that will cause to_ical to fail
        events = [{"title": "Test Event", "start_time": "invalid_date"}]
        output_path = tmp_path / "test.ics"

        success = exporter.export_ics_file(events, output_path)

        assert not success
        assert not output_path.exists()

    def test_parse_schedule_data_empty(self, exporter):
        """Test parsing empty schedule data."""
        events = exporter.parse_schedule_data({})

        assert len(events) == 0

    def test_parse_schedule_data_invalid_format(self, exporter):
        """Test parsing schedule data in invalid format."""
        events = exporter.parse_schedule_data("invalid format")

        assert len(events) == 0

    @pytest.mark.parametrize(
        "value,utc_hour",
        [
            ("2025-06-15T13:00:00Z", 13),
            ("2025-06-15T09:00:00-04:00", 13),
            ("2025-06-15T15:00:00+02:00", 13),
            ("2025-06-15 09:00:00", 13),
            ("2025-06-15T09:00:00", 13),
            ("2025-06-15 09:00", 13),
            ("2025-06-15T09:00", 13),
            ("2025-06-15", 4),
            (datetime(2025, 6, 15, 9), 13),
            (datetime(2025, 6, 15, 13, tzinfo=timezone.utc), 13),
        ],
    )
    def test_export_round_trips_instants_and_naive_timezone(self, tmp_path, value, utc_hour):
        exporter = ScheduleExporter({"timezone": "America/New_York"})
        output = tmp_path / "schedule.ics"
        output.write_bytes(b"previous calendar\r\n")
        assert exporter.export_symposium_schedule(
            [{"title": "Synthetic event", "start_time": value}], output
        )
        calendar = icalendar.Calendar.from_ical(output.read_bytes())
        events = [component for component in calendar.walk() if component.name == "VEVENT"]
        assert len(events) == 1
        expected = datetime(2025, 6, 15, utc_hour, tzinfo=timezone.utc)
        assert events[0].decoded("dtstart").astimezone(timezone.utc) == expected
        assert events[0].decoded("dtend").astimezone(timezone.utc) == expected + timedelta(hours=1)
        assert str(events[0]["summary"]) == "Synthetic event"
        assert set(tmp_path.iterdir()) == {output}

    @pytest.mark.parametrize("field", ["start_time", "end_time"])
    def test_invalid_timestamp_rejects_whole_publication(self, exporter, tmp_path, field):
        output = tmp_path / "schedule.ics"
        original = b"previous calendar\r\n"
        output.write_bytes(original)
        invalid = {
            "title": "Invalid event",
            "start_time": "2025-06-15T09:00:00Z",
            "end_time": "2025-06-15T10:00:00Z",
            field: "not-a-timestamp",
        }
        schedule = [
            {"title": "Valid event", "start_time": "2025-06-15T08:00:00Z"},
            invalid,
        ]
        assert not exporter.export_symposium_schedule(schedule, output)
        assert output.read_bytes() == original
        assert set(tmp_path.iterdir()) == {output}
        report = exporter.validate_schedule(schedule)
        assert report["valid_events"] == 1
        assert len(report["errors"]) == 1

    @pytest.mark.parametrize(
        "failure",
        [
            "construction",
            "serialization",
            "creation",
            "write",
            "short_write",
            "flush",
            "close",
            "sync",
            "replace",
        ],
    )
    def test_failed_publication_preserves_existing_bytes_and_other_temps(
        self, exporter, sample_schedule_data, tmp_path, monkeypatch, failure
    ):
        output = tmp_path / "schedule.ics"
        original = b"previous calendar\r\n\x00"
        output.write_bytes(original)
        unrelated = tmp_path / ".schedule.ics.someone-else.tmp"
        unrelated.write_bytes(b"not owned by this export")
        events = exporter.parse_schedule_data(sample_schedule_data)
        owned_temps = []

        def fail(*args, **kwargs):
            raise OSError("Synthetic publication failure")

        if failure == "construction":
            monkeypatch.setattr(exporter, "create_ics_calendar", fail)
        elif failure == "serialization":
            monkeypatch.setattr(icalendar.Calendar, "to_ical", fail)
        elif failure == "creation":
            monkeypatch.setattr(exporter_module, "NamedTemporaryFile", fail)
        elif failure in ("write", "short_write", "flush", "close"):
            create_temporary = exporter_module.NamedTemporaryFile

            class BrokenTemporary:
                def __init__(self, **kwargs):
                    self.file = create_temporary(**kwargs)
                    self.name = self.file.name
                    owned_temps.append(Path(self.name))

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    result = self.file.__exit__(*args)
                    if failure == "close":
                        raise OSError("Synthetic close failure")
                    return result

                def write(self, content):
                    if failure in ("write", "short_write"):
                        self.file.write(content[:7])
                        if failure == "short_write":
                            return 7
                        raise OSError("Synthetic partial write")
                    return self.file.write(content)

                def flush(self):
                    if failure == "flush":
                        raise OSError("Synthetic flush failure")
                    return self.file.flush()

                def fileno(self):
                    return self.file.fileno()

            monkeypatch.setattr(exporter_module, "NamedTemporaryFile", BrokenTemporary)
        elif failure == "sync":
            monkeypatch.setattr(exporter_module.os, "fsync", fail)
        else:
            monkeypatch.setattr(exporter_module.os, "replace", fail)

        assert not exporter.export_ics_file(events, output)
        assert output.read_bytes() == original
        assert unrelated.read_bytes() == b"not owned by this export"
        assert all(not path.exists() for path in owned_temps)
        assert set(tmp_path.iterdir()) == {output, unrelated}
