window.onload = function() {
    const loggedInUser = localStorage.getItem('loggedInUser');
    
    if (!loggedInUser) {
        alert("გთხოვთ შედით თქვენს ანგარიშზე.");
        window.location.href = '/login';  // Redirect to login page if not logged in
    } else {
        document.getElementById('username-span').textContent = loggedInUser;

        const profilePicture = localStorage.getItem(loggedInUser + '-profile-picture');
        if (profilePicture) {
            document.getElementById('profile-img').src = profilePicture;
        }

        const purchasedWorks = JSON.parse(localStorage.getItem(loggedInUser + '-purchased-works')) || [];
        const purchasedWorksList = document.getElementById('purchased-works-list');

        if (purchasedWorks.length > 0) {
            purchasedWorks.forEach(work => {
                const li = document.createElement('li');
                li.textContent = work;
                purchasedWorksList.appendChild(li);
            });
        } else {
            purchasedWorksList.innerHTML = '<li>არაფერი შეძენილი.</li>';
        }
    }

    // Profile Picture Upload
    document.getElementById('upload-picture-btn').addEventListener('click', function() {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        
        fileInput.addEventListener('change', function() {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imgSrc = e.target.result;
                    document.getElementById('profile-img').src = imgSrc;

                    localStorage.setItem(loggedInUser + '-profile-picture', imgSrc);
                };
                reader.readAsDataURL(file);
            }
        });

        fileInput.click();
    });

    // Logout Function
    document.getElementById('logout-btn').addEventListener('click', function() {
        fetch('/logout')  // Call Flask Logout Route
            .then(() => {
                localStorage.removeItem('loggedInUser');  // Remove user session from localStorage
                alert("თქვენ წარმატებით გამოხვედით!");
                window.location.href = '/login';  // Redirect to login page
            });
    });
};
