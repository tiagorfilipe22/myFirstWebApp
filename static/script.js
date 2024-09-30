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



// Array of available themes
const themes = ['light', 'dark', 'medium'];


// Function to toggle between themes
function toggleMode() {
  const currentTheme = getCurrentTheme(); // Get current theme
  const currentIndex = themes.indexOf(currentTheme); // Get index of current theme
  const newIndex = (currentIndex + 1) % themes.length; // Calculate next theme index
  const newTheme = themes[newIndex]; // Get the new theme

  // Swap the class on the html element
  document.documentElement.classList.remove(currentTheme);
  document.documentElement.classList.add(newTheme);

  // Store the new theme in localStorage
  localStorage.setItem('theme', newTheme);
}

// Function to get the current theme from the document
function getCurrentTheme() {
  for (const theme of themes) {
      if (document.documentElement.classList.contains(theme)) {
          return theme;
      }
  }
  return themes[0]; // Default to the first theme if none found
}

// Immediately apply the stored theme or default to 'light'
(function() {
  const savedTheme = localStorage.getItem('theme') || themes[0]; // Default to the first theme
  document.documentElement.classList.add(savedTheme); // Apply the theme early
})();



/*------------------------------------------*/

document.addEventListener('DOMContentLoaded', function() {
  // Get the active link ID from localStorage
  var activeLinkId = localStorage.getItem('activeLink');

  // Set default link if no active link is stored
  if (!activeLinkId) {
      activeLinkId = 'ticketID'; // Set default link ID here
  }

  // Add 'active' class to the stored link ID
  document.querySelectorAll('a').forEach(function(link) {
      if (link.id === activeLinkId) {
          link.classList.add('active');
      }
  });

  // Add event listener to the button with class 'logo'
  var logoButton = document.querySelector('.logo');
  if (logoButton) {
      logoButton.addEventListener('click', function() {
          resetActiveLink('ticketID'); // Reset to 'ticketID'
      });
  }

  // Add click event listeners to all links
  document.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', changeActiveLink);
  });
});

// Function to reset the active link
function resetActiveLink(linkId) {
  // Store the linkId in localStorage before navigating away
  localStorage.setItem('activeLink', linkId);
  
  // Use a timeout to allow the page to load before changing the active class
  setTimeout(function() {
      // Remove 'active' class from all links
      document.querySelectorAll('a').forEach(function(link) {
          link.classList.remove('active');
      });

      // Add 'active' class to the specified link ID
      document.getElementById(linkId).classList.add('active');
  }, 100); // Adjust the delay as necessary
}

function changeActiveLink(event) {
  var linkId = event.target.id;

  // Store the linkId in localStorage before navigating away
  localStorage.setItem('activeLink', linkId);
  
  // Use a timeout to allow the page to load before changing the active class
  setTimeout(function() {
      // Remove 'active' class from all links
      document.querySelectorAll('a').forEach(function(link) {
          link.classList.remove('active');
      });

      // Add 'active' class to the clicked link
      document.getElementById(linkId).classList.add('active');
  }, 100); // Adjust the delay as necessary
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