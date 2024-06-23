const submitButton = document.getElementById('submitButton');

submitButton.addEventListener('click', submitData);

function submitData() {
    // Get user input
    const userInput = document.getElementById('userInput').value;

    // Make sure there is input before sending the request
    if (!userInput) {
        alert("Please enter some text.");
        return;
    }

    // Define the data to be sent in JSON format
    const data = {
        "user_id": 1,
        "user_input": userInput
    };


    // Make a fetch request
    fetch('http://3.93.107.253:80', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Display the response in the label
        const responseLabel = document.getElementById('responseLabel');
        responseLabel.textContent = `${data.output}`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
