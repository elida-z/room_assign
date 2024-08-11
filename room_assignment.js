document.getElementById('roomForm').addEventListener('submit', function(event) {
    event.preventDefault();
    processFiles();
  });
  
  const defaultRooms = {
    "SARA ALRAWI": [1, 2, 4, 5, 9],
    "DR. LU": [3, 6, 7, 8],
    "PATRICK O'NEILL": [13, 14, 15, 16],
    "CAREY RYAN": [1, 2, 5, 13, 14, 15, 16],
    "KELLY KIRLES": [1, 2, 4, 5, 9]
  };
  
  const doubleRooms = new Set([3, 8, 15, 14, 5, 9]);
  
  function timeToDatetime(timeStr) {
    const [timePart, ampm] = timeStr.split(' ');
    const hour = timePart === '12:00' && ampm === 'AM' ? 0 : parseInt(timePart.split(':')[0]);
    const minutes = parseInt(timePart.split(':')[1]);
    const date = new Date();
    date.setHours(hour + (ampm === 'PM' ? 12 : 0), minutes, 0, 0);
    return date;
  }
  
  function readCombinedInputFile(content) {
   // ... (The rest of your `readCombinedInputFile`, `assignRooms`, `generateTextByRoom`, `generateTextByPractitioner`, and  `timeToDatetime` functions remain the same as the previous version) ...
  }
  
  // Function to process the uploaded files and display the output
  function processFiles() {
    const fileInput = document.getElementById('appointmentsFile');
    const file = fileInput.files[0];
  
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }
  
    const reader = new FileReader();
    reader.onload = function(event) {
      const content = event.target.result;
      const schedules = readCombinedInputFile(content);
  
      const [roomAssignments, practitionerAssignments] = assignRooms(
        schedules,
        defaultRooms
      );
  
      // Generate output text 
      const roomOutput = generateTextByRoom(roomAssignments);
      const practitionerOutput = generateTextByPractitioner(practitionerAssignments);
  
      // Display the output in the 'output' div 
      document.getElementById('output').innerHTML = `
        <h3>Appointments by Room</h3>
        <pre>${roomOutput}</pre> 
        <h3>Appointments by Practitioner</h3>
        <pre>${practitionerOutput}</pre>
      `; 
    };
  
    reader.readAsText(file);
  }