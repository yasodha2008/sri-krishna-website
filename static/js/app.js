let cart = JSON.parse(localStorage.getItem("sk_cart")) || [];

let wishlist =
    JSON.parse(localStorage.getItem("sk_wishlist")) || [];


/* SEARCH */

function focusSearch() {

    const search =
        document.querySelector(".search-container");

    search.classList.add("show");

    document
        .getElementById("searchInput")
        .focus();
}


function clearSearch() {

    document.getElementById(
        "searchInput"
    ).value = "";

    searchProducts();
}


function searchProducts() {

    const input =
        document.getElementById("searchInput");

    if (!input) return;

    const value =
        input.value.toLowerCase().trim();

    document
        .querySelectorAll(".product")
        .forEach(product => {

            const name =
                product.dataset.name || "";

            const category =
                product.dataset.category || "";

            product.style.display =
                (
                    name.includes(value) ||
                    category.includes(value)
                )
                ? ""
                : "none";
        });
}


/* CATEGORY */

function filterCategory(category) {

    category =
        category.toLowerCase();

    document
        .querySelectorAll(".product")
        .forEach(product => {

            const productCategory =
                product.dataset.category || "";

            product.style.display =
                productCategory.includes(category)
                    ? ""
                    : "none";
        });

    scrollToProducts();
}


function showAllProducts() {

    document
        .querySelectorAll(".product")
        .forEach(product => {

            product.style.display = "";
        });

    scrollToProducts();
}


/* CART */

function addToCart(
    id,
    name,
    price,
    image
) {

    let existing =
        cart.find(item => item.id == id);

    if (existing) {

        existing.quantity++;

    } else {

        cart.push({
            id: id,
            name: name,
            price: Number(price),
            image: image,
            quantity: 1
        });
    }

    saveCart();

    updateCart();

    openCart();
}


function saveCart() {

    localStorage.setItem(
        "sk_cart",
        JSON.stringify(cart)
    );
}


function updateCart() {

    const count =
        cart.reduce(
            (sum,item) =>
                sum + item.quantity,
            0
        );

    document.getElementById(
        "cartCount"
    ).innerText = count;

    renderCart();
}


function openCart() {

    document
        .getElementById("cartDrawer")
        .classList.add("open");

    document
        .getElementById("cartOverlay")
        .classList.add("open");

    renderCart();
}


function closeCart() {

    document
        .getElementById("cartDrawer")
        .classList.remove("open");

    document
        .getElementById("cartOverlay")
        .classList.remove("open");
}


function renderCart() {

    const container =
        document.getElementById("cartItems");

    if (!container) return;

    container.innerHTML = "";

    let total = 0;

    if (cart.length === 0) {

        container.innerHTML = `
            <div style="
                text-align:center;
                padding:70px 20px;
                color:#8c8387;
            ">
                <div style="font-size:50px;">
                    🛍
                </div>

                <h3 style="
                    font-family:'Playfair Display',serif;
                    margin:12px 0 5px;
                ">
                    Your bag is empty
                </h3>

                <p style="font-size:11px;">
                    Discover something beautiful.
                </p>
            </div>
        `;

        document.getElementById(
            "cartTotal"
        ).innerText = "₹0";

        return;
    }


    cart.forEach((item,index) => {

        total +=
            item.price *
            item.quantity;


        container.innerHTML += `

            <div style="
                display:flex;
                gap:12px;
                margin-bottom:20px;
            ">

                <img
                    src="${item.image || ''}"
                    style="
                        width:70px;
                        height:75px;
                        object-fit:cover;
                        border-radius:12px;
                        background:#f5e1e8;
                    "
                >

                <div style="flex:1;">

                    <strong style="
                        font-family:'Playfair Display',serif;
                        font-size:14px;
                    ">
                        ${item.name}
                    </strong>

                    <div style="
                        color:#a53662;
                        font-weight:700;
                        margin-top:5px;
                    ">
                        ₹${item.price}
                    </div>

                    <div style="
                        display:flex;
                        gap:8px;
                        align-items:center;
                        margin-top:8px;
                    ">

                        <button
                            onclick="changeQuantity(${index},-1)"
                            style="
                                width:25px;
                                height:25px;
                                border:1px solid #eee;
                                background:white;
                                border-radius:5px;
                            ">
                            −
                        </button>

                        ${item.quantity}

                        <button
                            onclick="changeQuantity(${index},1)"
                            style="
                                width:25px;
                                height:25px;
                                border:1px solid #eee;
                                background:white;
                                border-radius:5px;
                            ">
                            +
                        </button>

                    </div>

                </div>

            </div>
        `;
    });


    document.getElementById(
        "cartTotal"
    ).innerText = "₹" + total;
}


function changeQuantity(index,change) {

    cart[index].quantity += change;

    if (cart[index].quantity <= 0) {

        cart.splice(index,1);
    }

    saveCart();

    updateCart();
}


/* WISHLIST */

function addWishlist(id) {

    if (wishlist.includes(id)) {

        wishlist =
            wishlist.filter(
                item => item != id
            );

    } else {

        wishlist.push(id);
    }

    localStorage.setItem(
        "sk_wishlist",
        JSON.stringify(wishlist)
    );

    updateWishlist();
}


function updateWishlist() {

    document.getElementById(
        "wishlistCount"
    ).innerText = wishlist.length;
}


function toggleWishlist() {

    alert(
        "You have " +
        wishlist.length +
        " saved item(s)."
    );
}


/* FILTER */

function toggleFilters() {

    document
        .getElementById("filterPanel")
        .classList.toggle("show");
}


function applyFilters() {

    const colors =
        [...document.querySelectorAll(
            ".color-filter:checked"
        )].map(
            item => item.value
        );


    const price =
        document.querySelector(
            'input[name="price"]:checked'
        );


    document
        .querySelectorAll(".product")
        .forEach(product => {

            const color =
                product.dataset.color;

            const productPrice =
                Number(product.dataset.price);


            let colorMatch =
                colors.length === 0 ||
                colors.includes(color);


            let priceMatch = true;


            if (price) {

                if (price.value === "500") {

                    priceMatch =
                        productPrice < 500;

                } else if (
                    price.value === "1000"
                ) {

                    priceMatch =
                        productPrice >= 500 &&
                        productPrice <= 1000;

                } else {

                    priceMatch =
                        productPrice > 1000;
                }
            }


            product.style.display =
                colorMatch && priceMatch
                    ? ""
                    : "none";
        });
}


/* SORT */

function sortProducts() {

    const grid =
        document.getElementById(
            "productGrid"
        );

    let products =
        [...grid.querySelectorAll(
            ".product"
        )];


    const value =
        document.getElementById(
            "sortSelect"
        ).value;


    if (value === "low") {

        products.sort(
            (a,b) =>
                Number(a.dataset.price) -
                Number(b.dataset.price)
        );

    } else if (value === "high") {

        products.sort(
            (a,b) =>
                Number(b.dataset.price) -
                Number(a.dataset.price)
        );
    }


    products.forEach(
        item => grid.appendChild(item)
    );
}


/* SCROLL */

function scrollToProducts() {

    document
        .getElementById("trending")
        .scrollIntoView({
            behavior:"smooth"
        });
}


function scrollToOccasions() {

    document
        .getElementById("occasions")
        .scrollIntoView({
            behavior:"smooth"
        });
}


/* START */

updateCart();

updateWishlist();