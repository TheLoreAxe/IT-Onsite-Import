import pandas as pd
from datetime import datetime
from tkinter import Tk, filedialog
import os

APT_HOURS = {
    'KSI':     {'morning_start': '10:00', 'morning_end': '11:30', 'afternoon_start': '14:00', 'afternoon_end': '15:00'},
    'GPW':     {'morning_start': '10:30', 'morning_end': '14:00', 'afternoon_start': '10:30', 'afternoon_end': '14:00'}, # All day event so whichever slot is filled, it will put in all day
    'default': {'morning_start': '09:00', 'morning_end': '11:30', 'afternoon_start': '14:00', 'afternoon_end': '16:30'}
}

ONSITE_HOURS = {
    'KSI':     {'morning_start': '10:00', 'morning_end': '11:30', 'afternoon_start': '13:30', 'afternoon_end': '15:30'},
    'GPW':     {'morning_start': '10:00', 'morning_end': '15:00', 'afternoon_start': '10:00', 'afternoon_end': '15:00'}, # All day event so whichever slot is filled, it will put in all day
    'default': {'morning_start': '08:00', 'morning_end': '12:00', 'afternoon_start': '13:00', 'afternoon_end': '17:00'}
}

EMAILS = {
    'Matthew Steffan': 'mjsteffan99@gmail.com'
}

def read_csv(file_path):
    df = pd.read_csv(file_path, skiprows=2)
    required_columns = ['Date', 'AM Office', 'PM Office', 'Who']

    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    task_index = df[df['Date'].str.contains('TASKS', case=False, na=False)].index

    if not task_index.empty:
        df = df.iloc[:task_index[0]]

    df = df[df['Date'].notna() & ~df['Date'].astype(str).str.strip().eq('')]

    return df

def write_event(f, date, start_time, end_time, summary, status='CONFIRMED', attendee=None, transparent=False):
    transp_value = 'TRANSPARENT' if transparent else 'OPAQUE'
    f.write(f"""
BEGIN:VEVENT
DTSTART:{date.strftime('%Y%m%dT')}{start_time.replace(':', '')}00
DTEND:{date.strftime('%Y%m%dT')}{end_time.replace(':', '')}00
SUMMARY:{summary}
STATUS:{status}
TRANSP:{transp_value}
""".strip())

    if attendee and attendee in EMAILS:
        f.write(f"\nATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;CN={attendee};X-NUM-GUESTS=0:MAILTO:{EMAILS[attendee]}")

    f.write("\nEND:VEVENT\n")

def create_ics(events, onsite_file, core_file):
    with open(onsite_file, 'w') as onsite, open(core_file, 'w') as core:
        for f in (onsite, core):
            f.write("BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//My Python Script//EN\n")

        current_year  = datetime.now().year
        current_month = datetime.now().month

        for _, row in events.iterrows():
            try:
                date_str   = str(row['Date']).strip()
                date_parts = date_str.split('/')

                if len(date_parts) == 1:
                    date_str = f"{current_month}/{date_str}/{current_year}"
                elif int(date_parts[0]) < current_month:
                    date_str = f"{date_parts[0]}/{date_parts[1]}/{current_year + 1}"
                else:
                    date_str = f"{date_parts[0]}/{date_parts[1]}/{current_year}"

                date = datetime.strptime(date_str, '%m/%d/%Y').date()
            except Exception as e:
                print(f"Error parsing date {row['Date']}: {e}")
                continue

            attendees   = row['Who']
            am_location = row['AM Office']
            pm_location = row['PM Office']

            apt_am_hours = APT_HOURS.get(am_location, APT_HOURS['default']) if pd.notna(am_location) else None
            apt_pm_hours = APT_HOURS.get(pm_location, APT_HOURS['default']) if pd.notna(pm_location) else None

            # IT Onsite Calendar (Marked as Free)
            if am_location and apt_am_hours and am_location != 'PCO':
                write_event(onsite, date, apt_am_hours['morning_start'], apt_am_hours['morning_end'],
                            f"({am_location}) IT ONSITE", transparent=True)
            if pm_location and apt_pm_hours and pm_location != 'PCO':
                write_event(onsite, date, apt_pm_hours['afternoon_start'], apt_pm_hours['afternoon_end'],
                            f"({pm_location}) IT ONSITE", transparent=True)

            it_am_hours = ONSITE_HOURS.get(am_location, ONSITE_HOURS['default']) if pd.notna(am_location) else None
            it_pm_hours = ONSITE_HOURS.get(pm_location, ONSITE_HOURS['default']) if pd.notna(pm_location) else None

            # CORE IT Calendar
            if am_location and apt_am_hours:
                write_event(core, date, it_am_hours['morning_start'], it_am_hours['morning_end'],
                            f"({am_location}) IT ONSITE", attendee=attendees)
            if pm_location and apt_pm_hours:
                write_event(core, date, it_pm_hours['afternoon_start'], it_pm_hours['afternoon_end'],
                            f"({pm_location}) IT ONSITE", attendee=attendees)

        for f in (onsite, core):
            f.write("END:VCALENDAR")

def main():
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        print("No file selected. Exiting.")
        return

    base_path = os.path.dirname(file_path)
    onsite_file = os.path.join(base_path, 'it_onsite_events.ics')
    core_file   = os.path.join(base_path, 'core_it_events.ics')

    df = read_csv(file_path)
    create_ics(df, onsite_file, core_file)

    print(f"ICS files created:\n - {onsite_file}\n - {core_file}")

if __name__ == "__main__":
    main()
