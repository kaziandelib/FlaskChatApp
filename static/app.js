$(document).ready(function() {
    // Initialize the socket connection with the server
    var socket = io();

    // Event listener for incoming messages from the server
    socket.on('message', function(data){
        // Extract the username and message from the received data
        let username = data.username;
        let msg = data.msg;
        
        // Use backticks (template literals) to format and display the message in the chat box
        // It creates a new div element containing the message
        $("#chat-box").append(`<div><strong>${username}:</strong> ${msg}</div>`);
    });

    // Event listener for the "Send" button click
    $('#send-btn').on('click', function(){
        // Retrieve the value entered in the message input field
        var message = $('#message').val();
        
        // Send the message to the server using the socket connection
        socket.send(message);
        
        // After sending the message, clear the input field to prepare for the next message
        $('#message').val('');
    });

    // Event listener for the Enter key press while typing a message
    $('#message').keypress(function(e){
        // Check if the Enter key (key code 13) was pressed
        if (e.which == 13){
            // Trigger the "Send" button click event to send the message
            $("#send-btn").click();
            return false; // Prevent the default behavior (like form submission)
        }
    });
});
