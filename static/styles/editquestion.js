// Get the input element
const inputElement = document.getElementById("question_marks");
  
    // Add an event listener for when the input value changes
inputElement.addEventListener("change", () => {
      // Get the current value of the input
    const value = inputElement.value;
  
    // Check if the value is not a positive integer
    if (isNaN(value) || value <= 0 || !Number.isInteger(parseFloat(value))) {
        // Display an error message
    inputElement.setCustomValidity("Please enter a positive integer");
    } else {
        // Clear any previous error messages
    inputElement.setCustomValidity("");
    }
});
