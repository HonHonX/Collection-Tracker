document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM content loaded");

    const form = document.getElementById("edit-description-form");
    const descriptionInput = document.getElementById("description");
    const saveButton = document.getElementById("save-button");

    if (form && descriptionInput && saveButton) {
        // Initially disable the Save button
        saveButton.disabled = true;

        // Keep track of the original description value
        let originalDescription = descriptionInput.value.trim();

        // Enable/disable the Save button based on changes
        descriptionInput.addEventListener("input", function () {
            const currentDescription = descriptionInput.value.trim();
            if (currentDescription !== originalDescription) {
                saveButton.disabled = false;
            } else {
                saveButton.disabled = true;
            }
        });

        // Handle form submission
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            // Trim the input value before submitting
            const description = descriptionInput.value.trim();

            if (description === originalDescription) {
                console.log("No changes made to the description.");
                return; // No changes, so do not submit the form
            }

            // Make the POST request to update the description
            fetch(form.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: `description=${encodeURIComponent(description)}`,
            })
            .then((response) => response.json()) // Always expect JSON
            .then((data) => {
                // Log the server response for debugging
                console.log("Server response:", data);

                if (data.success) {
                    alert("Note saved successfully!");
                    originalDescription = description;  // Update the original description after success
                    saveButton.disabled = true;  // Disable the save button after successful save
                } else {
                    console.log("Error details:", data.error); // Log error details if any
                    alert(`Error saving the note: ${data.error || "Please try again."}`);
                }
            })
            .catch((error) => {
                // Log the error details if any occur during the fetch
                console.error("There was an error saving the note:", error);
                alert("Error saving the note. Please try again.");
            });
        });
    } else {
        console.warn("Required elements (form, descriptionInput, saveButton) not found.");
    }
});
