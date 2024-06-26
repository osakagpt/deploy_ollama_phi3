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
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const responseLabel = document.getElementById('responseLabel');
        
        function readStream() {
            return reader.read().then(({ done, value }) => {
                if (done) {
                    return;
                }
                const chunk = decoder.decode(value, { stream: true });
                responseLabel.textContent += chunk;
                return readStream();
            });
        }
        return readStream();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
