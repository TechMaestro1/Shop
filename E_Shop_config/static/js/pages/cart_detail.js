//  Dropdown menu (Remove from cart)
function myFunction(itemId) {
    let dropdown = document.getElementById("myDropdown" + itemId);
    let dropdowns = document.getElementsByClassName("dropdown-content");

    // Close any open dropdowns
    for (let i = 0; i < dropdowns.length; i++) {
        if (dropdowns[i].classList.contains('show') && dropdowns[i] !== dropdown) {
            dropdowns[i].classList.remove('show');
        }
    }

    // Open the clicked dropdown
    dropdown.classList.toggle("show");
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('.dropbtn')) {
        let dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            let openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}


// Auto input max count for product
function checkMaxQuantity(input) {
    let maxQuantity = parseInt(input.getAttribute('max'));
    let enteredValue = parseInt(input.value);

    if (enteredValue > maxQuantity) {
        input.value = maxQuantity;
    }
}
