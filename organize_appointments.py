from datetime import datetime

# List of known practitioner names
practitioner_names = [
    "Carey Ryan",
    "Dr. Lu",
    "Patrick O'Neill",
    "Kelly Kirles",
    "Sara AlRawi"
]

def organize_appointments(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    provider_dict = {}
    
    # Iterate through each line in the file
    for line in lines:
        line = line.strip()

        # Skip lines that don't start with a valid date in MM/DD/YYYY format or contain a known practitioner name
        if not line:
            continue

        # Check if the line ends with a date in the format MM/DD/YYYY
        parts = line.split()
        
        if len(parts) < 4:
            continue
        
        # Case 1: Date/Time at the beginning and Practitioner at the end
        try:
            # Check if the first part is a date
            date_time = ' '.join(parts[:3])
            datetime.strptime(date_time, '%m/%d/%Y %I:%M %p')

            # The practitioner should be at the end
            provider = ' '.join(parts[-2:])
            if provider in practitioner_names:
                # The rest is the patient's name
                contact = ' '.join(parts[3:-2])
                if provider not in provider_dict:
                    provider_dict[provider] = []
                provider_dict[provider].append((date_time, contact))
                continue  # Skip further processing for this line
        except ValueError:
            pass  # Not a date-time format, so it could be the other case

        # Case 2: Practitioner at the beginning and Date/Time at the end
        provider = ' '.join(parts[:2])
        if provider in practitioner_names:
            try:
                # Check if the last part is a date
                date_time = ' '.join(parts[-3:])
                datetime.strptime(date_time, '%m/%d/%Y %I:%M %p')

                # The rest is the patient's name
                contact = ' '.join(parts[2:-3])
                if provider not in provider_dict:
                    provider_dict[provider] = []
                provider_dict[provider].append((date_time, contact))
            except ValueError:
                continue  # Not a valid date-time format
    
    # Sort by time within each provider's appointments
    for provider in provider_dict:
        provider_dict[provider].sort(key=lambda x: datetime.strptime(x[0], '%m/%d/%Y %I:%M %p'))

    # Write to the output file
    with open(output_file, 'w') as file:
        for provider, records in provider_dict.items():
            file.write(f'{provider}:\n')
            for i, (date_time, contact) in enumerate(records, 1):
                dt = datetime.strptime(date_time, '%m/%d/%Y %I:%M %p')
                time = dt.strftime('%I:%M %p').lstrip('0')
                file.write(f'{i}. {time} - {contact}\n')
            file.write('\n')

# Example usage
organize_appointments('input_text.txt', 'output_text.txt')
