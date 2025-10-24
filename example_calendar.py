#!/usr/bin/env python3
"""
Example script demonstrating the calendar module functionality.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from symposium.calendar import ScheduleExporter

def main():
    """Demonstrate calendar export functionality."""
    print("🎯 Symposium Calendar Module Demo")
    print("=" * 40)

    # Create sample symposium schedule data
    schedule_data = {
        'events': [
            {
                'title': 'Registration & Welcome Coffee',
                'start_time': '2025-06-15 08:00:00',
                'description': 'Registration opens with welcome coffee and networking',
                'location': 'Conference Center Lobby',
                'category': 'Registration',
                'speakers': ['Staff']
            },
            {
                'title': 'Opening Keynote: The Future of Active Inference',
                'start_time': '2025-06-15 09:00:00',
                'description': 'Keynote address on the evolution and future directions of active inference research',
                'location': 'Main Auditorium',
                'category': 'Keynote',
                'speakers': ['Karl Friston'],
                'url': 'https://symposium.ai/keynote'
            },
            {
                'title': 'Morning Coffee Break',
                'start_time': '2025-06-15 10:30:00',
                'description': 'Coffee break and networking opportunity',
                'location': 'Exhibition Hall',
                'category': 'Break'
            },
            {
                'title': 'Active Inference in Cognitive Science',
                'start_time': '2025-06-15 11:00:00',
                'description': 'Technical session on cognitive applications of active inference',
                'location': 'Room A',
                'category': 'Technical Session',
                'speakers': ['Maxwell Ramstead', 'Inês Hipólito'],
                'tags': ['cognitive-science', 'active-inference']
            },
            {
                'title': 'Lunch & Poster Session',
                'start_time': '2025-06-15 12:30:00',
                'description': 'Lunch followed by poster presentations and discussions',
                'location': 'Grand Hall',
                'category': 'Lunch',
                'duration_hours': 2
            }
        ]
    }

    # Initialize exporter
    exporter = ScheduleExporter()

    # Validate schedule
    print("\n📋 Validating Schedule...")
    validation_report = exporter.validate_schedule(schedule_data['events'])
    print(f"   Total events: {validation_report['total_events']}")
    print(f"   Valid events: {validation_report['valid_events']}")
    print(f"   Conflicts detected: {len(validation_report['conflicts'])}")
    print(f"   Errors: {len(validation_report['errors'])}")

    # Export to ICS format
    print("\n💾 Exporting to ICS Calendar...")

    # Create output directory
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "symposium_schedule.ics"

    success = exporter.export_symposium_schedule(
        schedule_data,
        output_path,
        calendar_name="Active Inference Symposium 2025",
        description="Complete schedule for the Active Inference Symposium 2025"
    )

    if success:
        print(f"✅ Successfully exported calendar to: {output_path}")
        print(f"   File size: {output_path.stat().st_size} bytes")

        # Verify the file content
        print("\n📄 Calendar File Contents Preview:")
        print("-" * 30)
        with open(output_path, 'rb') as f:
            content = f.read()
            print(f"   ICS content length: {len(content)} bytes")
            print("   ✅ Calendar file created successfully!")

    else:
        print("❌ Failed to export calendar")

    # Demonstrate CSV export
    print("\n📊 Testing CSV Export...")

    # Create a CSV version of the schedule
    csv_path = output_dir / "schedule.csv"
    csv_content = """title,start_time,description,location,category,speakers,duration_hours
Workshop: Active Inference Basics,2025-06-16 09:00:00,Introduction to active inference concepts,Workshop Room A,Workshop,Chris Fields,3
Panel Discussion: Future Directions,2025-06-16 14:00:00,Panel on future research directions,Main Auditorium,Panel,Multiple Speakers,1.5
Closing Ceremony,2025-06-16 16:00:00,Closing remarks and farewell,Main Auditorium,Ceremony,Organizing Committee,1
"""

    with open(csv_path, 'w') as f:
        f.write(csv_content)

    csv_output_path = output_dir / "from_csv.ics"
    csv_success = exporter.export_from_csv(
        csv_path,
        csv_output_path,
        calendar_name="Symposium Additional Events"
    )

    if csv_success:
        print(f"✅ Successfully exported CSV schedule to: {csv_output_path}")
        print(f"   File size: {csv_output_path.stat().st_size} bytes")
    else:
        print("❌ Failed to export CSV schedule")

    print("\n🎉 Calendar module demonstration completed!")
    print(f"\n📁 Output files created in: {output_dir.absolute()}")

    # List created files
    print("\n📋 Created Files:")
    for file_path in output_dir.iterdir():
        print(f"   - {file_path.name}")

if __name__ == "__main__":
    main()



