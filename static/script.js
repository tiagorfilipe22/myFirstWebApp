function changeActiveStatus() {
    var x = document.getElementById("category").value;
    if (x == "newcategory") {
        document.getElementById("newcategory").disabled = false;
    }
    else {
        document.getElementById("newcategory").disabled = true;
    }

  }

// Function to toggle between light and dark modes
function toggleMode() {
    const currentMode = document.documentElement.classList.contains('light') ? 'light' : 'dark';
    const newMode = currentMode === 'light' ? 'dark' : 'light';
  
    // Swap the class on the html element
    document.documentElement.classList.remove(currentMode);
    document.documentElement.classList.add(newMode);
  
    // Store the new mode in localStorage
    localStorage.setItem('theme', newMode);
  }
  
  // Apply the theme based on stored preference when the page loads (redundant due to early script)
  //window.onload = function() {
  //  const savedTheme = localStorage.getItem('theme') || 'light';
  //  document.documentElement.classList.add(savedTheme);
  //};
  
  (function() {
    const savedTheme = localStorage.getItem('theme') || 'light'; // Default to 'light'
    document.documentElement.classList.add(savedTheme); // Apply the theme early
  })();