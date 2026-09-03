const filters = document.querySelectorAll(".filter");
const cards = document.querySelectorAll(".flower-card");

filters.forEach(filter => {

    filter.addEventListener("click", () => {

        filters.forEach(button => {
            button.classList.remove("active");
        });

        filter.classList.add("active");

        const selectedCategory =
            filter.getAttribute("data-filter");

        cards.forEach(card => {

            const category =
                card.getAttribute("data-category");

            if (
                selectedCategory === "all" ||
                category === selectedCategory
            ) {
                card.style.display = "block";
            } else {
                card.style.display = "none";
            }

        });

    });

});