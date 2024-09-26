//----------------------------------------------------------------
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



/*------------------------------------------*/

document.addEventListener('DOMContentLoaded', function() {
  // Get the active link ID from localStorage
  var activeLinkId = localStorage.getItem('activeLink');

  // Set default link if no active link is stored
  if (!activeLinkId) {
      activeLinkId = 'linkID'; // Set default link ID here
  }

  // Add 'active' class to the stored link ID and show all links
  document.querySelectorAll('a').forEach(function(link) {
      if (link.id === activeLinkId) {
          link.classList.add('active');
      }
      /* link.classList.remove('hidden'); */
  });
});

function changeActiveLink(event) {
  var linkId = event.target.id;

  // Remove 'active' class from all links
  /*var links = document.querySelectorAll('a');
  links.forEach(function(link) {
      link.classList.remove('active');
  });*/

  // Add 'active' class to the clicked link
  document.getElementById(linkId).classList.add('active');

  // Store the linkId in localStorage
  localStorage.setItem('activeLink', linkId);
}



/*----------------------------------*/

function logout() {
  // Clear localStorage
  localStorage.removeItem('activeLink');
}



/*----------------------*/


function clickButton() {
  document.getElementById('clickbutton').click();
}