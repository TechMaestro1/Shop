// Get image elements from the DOM
const cartImg = document.getElementById('cart');
searchImg = document.getElementById('search');
searchInputImg = document.getElementById('search-input');
logoImg = document.getElementById('logo');
menuImg = document.getElementById('menu');

const body = document.querySelector("body"),
    nav = document.querySelector("nav"),
    searchToggle = document.querySelector(".searchToggle"),
    sidebarOpen = document.querySelector(".sidebarOpen");


// Check if the user has set dark mode
let prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

// Set the image depending on the theme
function setImage() {
    if (prefersDark) {
        cartImg.src = staticUrl + "img/cart.png";
        logoImg.src = staticUrl + "img/logo.png";
        searchImg.src = staticUrl + "img/search.png";
        searchInputImg.src = staticUrl + "img/search.png";
        menuImg.src = staticUrl + "img/menu.png";

    } else {
        cartImg.src = staticUrl + "img/cart_dark.png";
        logoImg.src = staticUrl + "img/logo_dark.png";
        searchImg.src = staticUrl + "img/search_dark.png";
        searchInputImg.src = staticUrl + "img/search_dark.png";
        menuImg.src = staticUrl + "img/menu_dark.png";
    }
}

setImage();

// Check if the dark mode  => and apply it
let getMode = localStorage.getItem("mode");
if (getMode && getMode === "dark-mode") {
    body.classList.add("dark");
}

// Get element from the DOM
let subMenu = document.getElementById("subMenu");

// When the user clicks on the menu button open it
function toggleMenu() {
    subMenu.classList.toggle("open-menu");
    searchToggle.classList.remove("active");
}

// Change Searchbar active state
searchToggle.addEventListener("click", () => {
    searchToggle.classList.toggle("active");
    subMenu.classList.remove("open-menu");
});

// If the user clicks outside of it => close menu
body.addEventListener("click", e => {
    let clickedElm = e.target;
    if (!clickedElm.classList.contains("sidebarOpen") && !clickedElm.classList.contains("menu")) {
        nav.classList.remove("active");
    }
});
searchToggle.classList.contains("sidebar")

// Open menu for small device
sidebarOpen.addEventListener("click", () => {
    nav.classList.add("active");
    searchToggle.classList.remove("active");
    subMenu.classList.remove("open-menu");
});

// If the user clicks outside of it => close submenu
const searchBox = document.querySelector('.searchBox');
document.addEventListener('click', function (event) {
    const isClickInsideSearchBox = searchBox.contains(event.target);
    if (!isClickInsideSearchBox) {
        subMenu.classList.remove('open-menu');
        searchToggle.classList.remove('active');

    }
});


// Listen for theme changes and update images accordingly
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    prefersDark = e.matches;
    setImage();
});