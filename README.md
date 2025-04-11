# IT-Onsite-Import
Python script to take a specifically formatted csv and creates two .ics files that can be imported into a google calendar.  This was a response to automate the creation of IT Onsite calendar events for a company.

The CSV is always in the same format. See example CSV.

Each office has two calendars. One showing what time the IT department arrives at the office and one showing appointment availibility. Some offices have custom times due to the distance traveled. In the .csv, one column hosts if the time is in the morning and the other column lists if they are in the afternoon. 

The output is two .ics files. One will be imported into the IT calendar to show when we will be there. The other will be imported into the Appointments calendar to show what time we are accepting appointments. 

Example .csv format
![image](https://github.com/user-attachments/assets/37cffa75-ec7e-4310-9a1c-245580832061)

Output:
![image](https://github.com/user-attachments/assets/255285a3-e261-46c1-8a97-0edf3f12c95b)
