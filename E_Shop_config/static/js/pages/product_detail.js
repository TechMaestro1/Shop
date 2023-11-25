// Set index for photo Slider
let slideIndex = 1;
showSlides(slideIndex);

// Function to move to the next or previous slide
function plusSlides(n) {
    showSlides(slideIndex += n);
}

// Function to display the slides
function showSlides(n) {
    let i;
    // Get all the slide elements
    let slides = document.getElementsByClassName("mySlides");

    // If the index is greater than the number of slides, set it to 1
    if (n > slides.length) {
        slideIndex = 1
    }

    // If the index is less than 1, set it to the last slide
    if (n < 1) {
        slideIndex = slides.length
    }

    // Hide all the slides
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex - 1].style.display = "block";
}
