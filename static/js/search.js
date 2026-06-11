// ---------------- MENU TOGGLE ----------------

function toggleMenu() {

    let menu =
        document.getElementById("menu");

    if (menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}

// ---------------- HIDE WELCOME BOX ----------------

window.onload = function() {

    let welcomeBox =
        document.getElementById("welcomeBox");

    if (welcomeBox) {

        setTimeout(function() {

            welcomeBox.style.display = "none";

        }, 5000);
    }
};

// ---------------- LIVE SEARCH ----------------

function searchProducts() {

    let input =
        document.getElementById("searchInput");

    let filter =
        input.value.toUpperCase();

    let cards =
        document.getElementsByClassName("card");

    for (let i = 0; i < cards.length; i++) {

        let title =
            cards[i].getElementsByTagName("h3")[0];

        let txt =
            title.textContent || title.innerText;

        if (txt.toUpperCase().indexOf(filter) > -1) {

            cards[i].style.display = "";

        } else {

            cards[i].style.display = "none";

        }
    }
}

// ---------------- DELETE CONFIRM ----------------

function deleteProduct() {

    return confirm(
        "Are you sure you want to delete this product?"
    );
}