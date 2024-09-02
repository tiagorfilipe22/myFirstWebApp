function changeActiveStatus() {
    var x = document.getElementById("category").value;
    if (x == "newcategory") {
        document.getElementById("newcategory").disabled = false;
    }
    else {
        document.getElementById("newcategory").disabled = true;
    }

  }