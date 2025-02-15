// login.js

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent form submission

    // Get the username and password values
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    // Validate input (basic check)
    if (username === '' || password === '') {
        alert("გთხოვთ შეავსოთ ყველა ველი!");
        return;
    }

    // Get the users from localStorage
    let users = JSON.parse(localStorage.getItem('users')) || [];

    // Check if the username and password match
    const user = users.find(user => user.username === username && user.password === password);

    if (user) {
        // If user is found, log them in and redirect to the main page
        alert("შევიდა წარმატებით!");
        localStorage.setItem('loggedInUser', username);  // Store logged-in user
        window.location.href = 'index.html';  // Redirect to the main page after successful login
    } else {
        alert("არასწორი სახელი ან პაროლი!");
    }
});
