document.getElementById('photo-input').addEventListener('change', function (event) {
    loadUserPhoto(event);
});


// Show chosen photo
function loadUserPhoto(event) {
    let reader = new FileReader();
    reader.onload = function () {
        var output = document.getElementById('user-photo');
        output.src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
}


