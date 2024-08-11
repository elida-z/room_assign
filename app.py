import os
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, flash

from organize_appointments import organize_appointments  # Import function

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ensure this is set to a strong random value

# Define the default room mappings
default_rooms = {
    "SARA ALRAWI": [1, 2, 4, 5, 9],
    "DR. LU": [3, 6, 7, 8],
    "PATRICK O'NEILL": [13, 14, 15, 16],
    "CAREY RYAN": [1, 2, 5, 13, 14, 15, 16],
    "KELLY KIRLES": [1, 2, 4, 5, 9]
}

# Define double rooms
double_rooms = {3, 8, 15, 14, 5, 9}

# Helper function to convert time strings to datetime objects
def time_to_datetime(time_str):
    if time_str[-1] in ["a", "p"]:
        time_str = time_str[:-1] + " " + time_str[-1] + "m"
    try:
        return datetime.strptime(time_str, "%I:%M %p")
    except ValueError:
        return datetime.strptime(time_str, "%I %p")

# Function to read and parse the formatted input
def read_combined_input_file(lines):
    schedules = defaultdict(list)
    current_practitioner = None
    for line in lines:
        line = line.strip()
        if line.endswith(":"):
            current_practitioner = line[:-1].upper()
        elif line and current_practitioner:
            if "DO NOT SCHEDULE" in line:
                schedules[current_practitioner].append(("DO NOT SCHEDULE", ""))
            else:
                time_slot, patient = line.split(' - ', 1)
                time_slot = time_slot.split('. ', 1)[1].strip() if '. ' in time_slot else time_slot.strip()
                schedules[current_practitioner].append((time_slot, patient))
    return schedules

# Function to assign rooms with time gap constraint
def assign_rooms(schedules, rooms):
    room_assignments = defaultdict(list)
    practitioner_assignments = defaultdict(list)
    last_used_time = defaultdict(dict)
    double_booked = defaultdict(lambda: defaultdict(list))

    for practitioner, appointments in schedules.items():
        time_slot_counts = defaultdict(int)
        for time_slot, _ in appointments:
            time_slot_counts[time_slot] += 1

        for time_slot, patient in appointments:
            if "DO NOT SCHEDULE" in time_slot:
                continue
            time_obj = time_to_datetime(time_slot)
            assigned = False

            if time_slot_counts[time_slot] > 1:
                double_booked[practitioner][time_slot].append(patient)
                if len(double_booked[practitioner][time_slot]) == 2:
                    for room in rooms[practitioner]:
                        if room in double_rooms:
                            required_gap = (
                                timedelta(minutes=60)
                                if practitioner == "DR. LU"
                                else timedelta(minutes=75)
                            )
                            if (
                                room not in last_used_time[practitioner]
                                or time_obj
                                >= last_used_time[practitioner][room] + required_gap
                            ):
                                patients = ", ".join(
                                    double_booked[practitioner][time_slot]
                                )
                                room_assignments[room].append(
                                    (time_slot, practitioner, patients)
                                )
                                practitioner_assignments[practitioner].append(
                                    (time_slot, patients, room)
                                )
                                last_used_time[practitioner][room] = time_obj
                                assigned = True
                                break
                        if assigned:
                            break
            else:
                for room in rooms[practitioner]:
                    required_gap = (
                        timedelta(minutes=60)
                        if practitioner == "DR. LU"
                        else timedelta(minutes=75)
                    )
                    if (
                        room not in last_used_time[practitioner]
                        or time_obj >= last_used_time[practitioner][room] + required_gap
                    ):
                        room_assignments[room].append(
                            (time_slot, practitioner, patient)
                        )
                        practitioner_assignments[practitioner].append(
                            (time_slot, patient, room)
                        )
                        last_used_time[practitioner][room] = time_obj
                        assigned = True
                        break
            if not assigned and time_slot_counts[time_slot] == 1:
                print(f"Warning: No available room for {practitioner} at {time_slot}")

    return room_assignments, practitioner_assignments

# Function to generate the text output by room
def generate_text_by_room(room_assignments):
    output = ""
    for room in sorted(room_assignments.keys()):
        output += f"Room {room}:\n"
        for (
            time_slot,
            practitioner,
            patient,
        ) in sorted(
            room_assignments[room], key=lambda x: time_to_datetime(x[0])
        ):
            output += f"{time_slot} - {practitioner}: {patient}\n"
        output += "\n"
    return output

# Function to generate the text output by practitioner and time
def generate_text_by_practitioner(practitioner_assignments):
    output = ""
    for practitioner in sorted(practitioner_assignments.keys()):
        output += f"{practitioner.title()}:\n"
        for (
            i,
            (time_slot, patient, room),
        ) in enumerate(
            sorted(
                practitioner_assignments[practitioner],
                key=lambda x: time_to_datetime(x[0]),
            ),
            1,
        ):
            output += f"{i}. {time_slot} - Room {room}: {patient}\n"
        output += "\n"
    return output

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        # Handle file upload
        file = request.files['appointmentsFile']
        if file:
            file.save('input_text.txt')  # Save uploaded file as input_text.txt 
            organize_appointments('input_text.txt', 'output_text.txt')  

            # Immediately read output_text.txt
            with open('output_text.txt', 'r') as f:
                organized_output = f.read()

            # Parse the room numbers from the form
            updated_rooms = {}
            for practitioner in default_rooms.keys():
                room_numbers = request.form.get(f'{practitioner}_rooms')
                if room_numbers:
                    updated_rooms[practitioner] = list(map(int, room_numbers.split(',')))
                else:
                    updated_rooms[practitioner] = default_rooms[practitioner]

            schedules = read_combined_input_file(organized_output.splitlines())
            room_assignments, practitioner_assignments = assign_rooms(schedules, updated_rooms)

            room_output = generate_text_by_room(room_assignments)
            practitioner_output = generate_text_by_practitioner(practitioner_assignments)

            return render_template('index.html',
                                    room_output=room_output,
                                    practitioner_output=practitioner_output,
                                    rooms=updated_rooms)
    else:
        # For GET (or if no file): Display default form with room numbers
        return render_template('index.html', 
                                room_output="", 
                                practitioner_output="",
                                rooms=default_rooms)

@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_text = request.form.get('feedback')
    if feedback_text:
        print("Feedback received:", feedback_text)
        flash("Thank you for your feedback!")
    else:
        flash("Feedback cannot be empty.")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
