document.addEventListener("DOMContentLoaded", function() {
    // Handle login button click
    document.getElementById('login-button').addEventListener('click', function() {
        var nextUrl = "/";
        window.location.href = "/accounts/login/?next=" + encodeURIComponent(nextUrl);
    });

    // Handle register button click
    document.getElementById('register-button').addEventListener('click', function() {
        var nextUrl = window.location.pathname + window.location.search;
        window.location.href = "/register/?next=" + encodeURIComponent(nextUrl);
    });
});
