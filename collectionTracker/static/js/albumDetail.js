document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM content loaded");

    const form = document.getElementById("edit-description-form");
    const descriptionInput = document.getElementById("description");
    const saveButton = document.getElementById("save-button");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    if (form && descriptionInput && saveButton) {
        saveButton.disabled = true; 
        let originalDescription = descriptionInput.value.trim();

        descriptionInput.addEventListener("input", function () {
            const currentDescription = descriptionInput.value.trim();
            // Enable the Save button if the description changes (even if it's empty)
            saveButton.disabled = currentDescription === originalDescription;
        });

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            let description = descriptionInput.value.trim();

            // Save the description even if it's empty
            if (description === originalDescription) {
                console.log("No changes made to the description.");
                return;
            }

            updateServer(form.action, { description: description })
                .then((data) => {
                    if (data.success) {
                        alert("Note saved successfully!");
                        originalDescription = description;  // Update the original description to reflect the saved value
                        saveButton.disabled = true; // Disable the save button again
                    } else {
                        alert(`Error saving the note: ${data.error || "Please try again."}`);
                    }
                })
                .catch((error) => {
                    console.error("There was an error saving the note:", error);
                    alert("Error saving the note. Please try again.");
                });
        });
    } else {
        console.warn("Required elements (form, descriptionInput, saveButton) not found.");
    }

    const priorityForm = document.getElementById("priority-form");
    const prioritySelect = document.getElementById("priority");

    if (priorityForm && prioritySelect) {
        priorityForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const selectedPriority = prioritySelect.value;

            updateServer(priorityForm.action, { priority: selectedPriority })
                .then((data) => {
                    if (data.success) {
                        alert("Priority updated successfully!");
                        // Display the priority's human-readable name
                        const priorityLabel = document.getElementById("priority-label");
                        if (priorityLabel) {
                            priorityLabel.textContent = `Priority: ${data.priority_display}`;
                        }
                    } else {
                        alert(`Error updating priority: ${data.error || "Please try again."}`);
                    }
                })
                .catch((error) => {
                    console.error("There was an error updating the priority:", error);
                    alert("Error updating priority. Please try again.");
                });
        });
    } else {
        console.warn("Required elements (priorityForm, prioritySelect) not found.");
    }

     // Handle substatus update form
     const substatusForm = document.getElementById("substatus-form");
     const substatusSelect = document.getElementById("substatus");
 
    if (substatusForm && substatusSelect) {
        substatusForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const selectedSubstatus = substatusSelect.value;
            console.log(selectedSubstatus);

            updateServer(substatusForm.action, { substatus: selectedSubstatus })
                .then((data) => {
                    if (data.success) {
                        alert("Substatus updated successfully!");
                        console.log(selectedSubstatus)
                        const substatusLabel = document.getElementById("substatus-label");
                        if (substatusLabel) {
                            substatusLabel.textContent = `Substatus: ${data.substatus_display}`;
                        }
                    } else {
                        alert(`Error updating substatus: ${data.error || "Please try again."}`);
                    }
                })
                .catch((error) => {
                    console.error("There was an error updating the substatus:", error);
                    alert("Error updating substatus. Please try again.");
                });
        });
    } else {
        console.warn("Required elements (substatusForm, substatusSelect) not found.");
    }
     
    function updateServer(url, params) {
        const body = new URLSearchParams(params).toString();
        return fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": csrfToken,
            },
            body: body,
        }).then((response) => response.json());
    }
});
