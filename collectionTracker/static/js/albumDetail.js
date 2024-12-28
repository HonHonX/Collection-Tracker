document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("edit-description-form");
    const descriptionInput = document.getElementById("description"); // Textarea element
    const saveButton = document.getElementById("save-button"); // Save button

    if (form && descriptionInput && saveButton) {
        // Initially disable the Save button
        saveButton.disabled = true;

        // Keep track of the original description value
        let originalDescription = descriptionInput.value.trim();

        // Enable/disable the Save button based on changes
        descriptionInput.addEventListener("input", function () {
            const currentDescription = descriptionInput.value.trim();
            if (currentDescription !== originalDescription) {
                saveButton.disabled = false; // Enable the button if there's a change
            } else {
                saveButton.disabled = true; // Disable the button if unchanged
            }
        });

        // Handle form submission
        form.addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent the default form submission (which causes page reload)

            const description = descriptionInput.value.trim(); // Get the trimmed value from the textarea

            fetch(form.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: `description=${encodeURIComponent(description)}`,
            })
                .then((response) => {
                    // Check if the response is OK (status 200) and if it's JSON
                    if (!response.ok) {
                        throw new Error("Server responded with an error: " + response.status);
                    }

                    return response.json(); // Parse the response as JSON
                })
                .then((data) => {
                    if (data.success) {
                        // Show a success alert
                        alert("Note saved successfully!");
                        // Update the original description and disable the Save button
                        originalDescription = description;
                        saveButton.disabled = true;
                    } else {
                        alert("Error saving the note: " + (data.error || "Please try again."));
                    }
                })
                .catch((error) => {
                    console.error("There was an error saving the note:", error);
                    alert("Error saving the note. Please try again.");
                });
        });
    } else {
        console.error("Form, description input, or save button is missing from the DOM.");
    }
});
