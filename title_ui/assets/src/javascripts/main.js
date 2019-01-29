import './modules/govuk-frontend'
import './modules/cookie-banner'

var links = document.getElementsByClassName("charge-link");
for (let i = 0; i < links.length; i++) {
    links[i].onmouseover = function() {
        document.getElementById(this.getAttribute("href").substring(1)).parentNode.classList.add('highlighted-charge');
    }
    links[i].onmouseout = function() {
        document.getElementById(this.getAttribute("href").substring(1)).parentNode.classList.remove('highlighted-charge');
    }
}

window.onload = function() {
    if (window.location.hash) {
        document.getElementById(window.location.hash).parentNode.classList.remove('highlighted-charge');
    }
}