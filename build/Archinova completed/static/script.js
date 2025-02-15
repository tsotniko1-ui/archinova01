document.addEventListener("DOMContentLoaded", function () {
    const uploadForm = document.getElementById("upload-photo-form");
    const profilePhotoInput = document.getElementById("profile-photo");
    const profileImg = document.getElementById("profile-img");

    uploadForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const file = profilePhotoInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append("profile_pic", file);

            fetch("/upload_profile_pic", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    profileImg.src = "/static/profile_pics/" + data.filename;
                } else {
                    alert("ატვირთვის შეცდომა");
                }
            })
            .catch(error => console.error("პროფილის ფოტოს ატვირთვის შეცდომა:", error));
        }
    });
});






document.querySelectorAll(".bid-form").forEach(form => {
    form.addEventListener("submit", function(event) {
        event.preventDefault();

        const auctionId = this.dataset.auctionId;
        const bidAmount = this.querySelector("input[name='bid-amount']").value;

        fetch("{{ url_for('place_bid') }}", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"  // ✅ Ensures Flask knows it's JSON
            },
            body: JSON.stringify({
                auction_id: auctionId,
                amount: bidAmount
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("📩 Server response:", data);
            if (data.success) {
                const bidList = document.getElementById(`bids-list-${auctionId}`);
                const newBid = document.createElement("li");
                newBid.textContent = `${data.username}: ${data.amount} ₾`;
                bidList.appendChild(newBid);
            } else {
                alert("❌ ბიდის დადება ვერ მოხერხდა! Error: " + data.error);
            }
        })
        .catch(error => console.error("⚠️ Error placing bid:", error));
    });
});




document.addEventListener("DOMContentLoaded", function() {
    fetch("/get_user")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("User data received:", data); // ✅ Debugging
            if (data.username && data.email) {  // 🔹 აქ გამოვასწორე `name` -> `username`
                document.getElementById("seller-name").value = data.username;
                document.getElementById("seller-email").value = data.email;
            } else {
                console.warn("User data is missing required fields:", data);
            }
        })
        .catch(error => console.error("Error fetching user data:", error));
});

