
// change active field select "New Category"
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
const themes = ['Light', 'Dark'];

// Function to get the current theme from the document
function getCurrentTheme() {
  for (const theme of themes) {
      if (document.documentElement.classList.contains(theme)) {
          return theme;
      }
  }
  return themes[0]; // Default to the first theme if none found
}

// change Theme button name
function changeName(theme) {
  const button = document.getElementById('theme');
  if (button.textContent !== theme) {
    button.textContent = theme; // Set button text to the current theme
  }
}

// load at refresh
window.onload = function() {
  const currentTheme = getCurrentTheme();
  const currentIndex = themes.indexOf(currentTheme);
  const newIndex = (currentIndex + 1) % themes.length;
  const newTheme = themes[newIndex];

  changeName(newTheme)
}



// Function to toggle between themes
function toggleMode() {
  const currentTheme = getCurrentTheme();
  const currentIndex = themes.indexOf(currentTheme);
  const newIndex = (currentIndex + 1) % themes.length;
  const newTheme = themes[newIndex];

  
  changeName(currentTheme)


  // change the class on the html element
  document.documentElement.classList.remove(currentTheme);
  document.documentElement.classList.add(newTheme);

  // Store the new theme in localStorage
  localStorage.setItem('theme', newTheme);
}


// Immediately apply the stored theme or default to 'light'
(function() {
  const savedTheme = localStorage.getItem('theme') || themes[0]; // Default to the first theme
  document.documentElement.classList.add(savedTheme); 
})();



// change active link menu
document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('a');
  const defaultLinkId = localStorage.getItem('setDefault');
  const activeLinkId = localStorage.getItem('activeLink') || defaultLinkId;

  setActiveLink(activeLinkId);

  document.querySelector('.logo')?.addEventListener('click', () => setActiveLink(defaultLinkId));
  links.forEach(link => link.addEventListener('click', () => setActiveLink(link.id)));

  function setActiveLink(linkId) {
      localStorage.setItem('activeLink', linkId);
      links.forEach(link => link.classList.toggle('active', link.id === linkId));
  }
});


// when logout remove activeLink
function logout() {
  localStorage.removeItem('activeLink');
}


// set the default item
function setDefault(){
  localStorage.setItem('setDefault', 'ticketID');
  return
}

// clear the default item
function removesDefault(){
  localStorage.setItem('setDefault', '');
  return
}


// press button on click
function clickButton() {
  document.getElementById('clickbutton').click();
}

// press button with ID
function clickButtonID(Id) {
  document.getElementById('clickbuttonid-' + Id).click();
}


