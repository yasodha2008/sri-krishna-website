
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from database import get_supabase
from urllib.parse import quote


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = "sri_krishna_flower_shop_2026"


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = "https://qajajtijyhnabknjhwvk.supabase.co"

SUPABASE_BUCKET = "project-images"


# =========================================================
# CATEGORY FOLDERS
# =========================================================

CATEGORY_FOLDERS = {

    "Bouquet": "bouquet",

    "Crown": "crown",

    "Hair Decoration": "hair-decoration",

    "Hall Decoration": "hall-decoration",

    "Temple Sculpture Decoration":
        "temple-sculpture-decoration",

    "Flower Kolams": "flower-kolams",

    "Large Garlands": "large-garlands",

    "Money Garlands": "money-garlands",

    "Wedding Garlands": "wedding-garlands",

    "Stage Decorations": "stage-decorations"

}


# =========================================================
# IMAGE URL
# =========================================================

def get_supabase_image_url(folder, filename):

    if not folder or not filename:
        return ""

    folder = CATEGORY_FOLDERS.get(
        folder,
        folder
    )

    return (
        f"{SUPABASE_URL}"
        f"/storage/v1/object/public/"
        f"{SUPABASE_BUCKET}/"
        f"{quote(folder, safe='')}/"
        f"{quote(filename, safe='')}"
    )


# =========================================================
# LANGUAGE PAGE
# =========================================================

@app.route("/")
def language():

    return render_template(
        "language.html"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/home")
def home():

    lang = request.args.get(
        "lang",
        "en"
    )

    if lang not in ["en", "ta"]:
        lang = "en"


    category = request.args.get(
        "category",
        "all"
    )


    supabase = get_supabase()


    # -----------------------------------------------------
    # GET CATEGORIES
    # -----------------------------------------------------

    try:

        result = (
            supabase
            .table("categories")
            .select("id, name, name_tamil")
            .order("id")
            .execute()
        )

        db_categories = result.data or []

    except Exception as error:

        print(
            "CATEGORY ERROR:",
            error
        )

        db_categories = []


    categories = []


    for item in db_categories:

        english_name = item.get(
            "name",
            ""
        )

        tamil_name = item.get(
            "name_tamil",
            ""
        )


        if lang == "ta" and tamil_name:

            display_name = tamil_name

        else:

            display_name = english_name


        categories.append({

            "id": item.get("id"),

            "name": english_name,

            "name_tamil": tamil_name,

            "display_name": display_name

        })


    # -----------------------------------------------------
    # GET PHOTOS
    # -----------------------------------------------------

    try:

        if category == "all":

            result = (
                supabase
                .table("photos")
                .select("*")
                .order(
                    "uploaded_at",
                    desc=True
                )
                .execute()
            )

        else:

            try:

                category_id = int(
                    category
                )

            except:

                category_id = None


            selected_category = next(

                (
                    item

                    for item in db_categories

                    if item.get("id")
                    == category_id

                ),

                None

            )


            if selected_category:

                category_name = (
                    selected_category
                    .get("name")
                )


                result = (
                    supabase
                    .table("photos")
                    .select("*")
                    .eq(
                        "flower_type",
                        category_name
                    )
                    .order(
                        "uploaded_at",
                        desc=True
                    )
                    .execute()
                )

            else:

                result = None


        if result:

            photos = result.data or []

        else:

            photos = []


    except Exception as error:

        print(
            "PHOTO ERROR:",
            error
        )

        photos = []


    # -----------------------------------------------------
    # IMAGE URLS
    # -----------------------------------------------------

    for photo in photos:

        if not photo.get("image_url"):

            photo["image_url"] = (
                get_supabase_image_url(

                    photo.get(
                        "flower_type"
                    ),

                    photo.get(
                        "filename"
                    )

                )
            )


    # -----------------------------------------------------
    # CART COUNT
    # -----------------------------------------------------

    cart = session.get(
        "cart",
        []
    )


    cart_count = sum(

        item.get(
            "quantity",
            1
        )

        for item in cart

    )


    return render_template(

        "home.html",

        lang=lang,

        category=category,

        categories=categories,

        photos=photos,

        cart_count=cart_count

    )


# =========================================================
# CART PAGE
# =========================================================

@app.route("/cart")
def cart():

    lang = request.args.get(
        "lang",
        "en"
    )

    if lang not in ["en", "ta"]:
        lang = "en"


    cart_items = session.get(
        "cart",
        []
    )


    total_items = sum(

        item.get(
            "quantity",
            1
        )

        for item in cart_items

    )


    return render_template(

        "cart.html",

        cart_items=cart_items,

        total_items=total_items,

        lang=lang

    )


# =========================================================
# ADD TO CART
# =========================================================

@app.route(
    "/add-to-cart",
    methods=["GET", "POST"]
)
def add_to_cart():

    # -----------------------------------------------------
    # PHOTO ID
    # -----------------------------------------------------

    photo_id = request.args.get(
        "photo_id"
    )


    if not photo_id:

        photo_id = request.form.get(
            "photo_id"
        )


    # -----------------------------------------------------
    # LANGUAGE
    # -----------------------------------------------------

    lang = request.args.get(
        "lang"
    )


    if not lang:

        lang = request.form.get(
            "lang",
            "en"
        )


    if lang not in ["en", "ta"]:

        lang = "en"


    # -----------------------------------------------------
    # CHECK ID
    # -----------------------------------------------------

    if not photo_id:

        return redirect(
            f"/home?lang={lang}"
        )


    try:

        photo_id = int(
            photo_id
        )

    except:

        return redirect(
            f"/home?lang={lang}"
        )


    # -----------------------------------------------------
    # SUPABASE
    # -----------------------------------------------------

    supabase = get_supabase()


    # -----------------------------------------------------
    # GET PHOTO
    # -----------------------------------------------------

    try:

        result = (
            supabase
            .table("photos")
            .select("*")
            .eq(
                "id",
                photo_id
            )
            .limit(1)
            .execute()
        )

        photos = result.data or []

    except Exception as error:

        print(
            "ADD CART ERROR:",
            error
        )

        return redirect(
            f"/home?lang={lang}"
        )


    if not photos:

        return redirect(
            f"/home?lang={lang}"
        )


    photo = photos[0]


    # -----------------------------------------------------
    # IMAGE
    # -----------------------------------------------------

    if not photo.get("image_url"):

        photo["image_url"] = (
            get_supabase_image_url(

                photo.get(
                    "flower_type"
                ),

                photo.get(
                    "filename"
                )

            )
        )


    # -----------------------------------------------------
    # CART
    # -----------------------------------------------------

    cart = session.get(
        "cart",
        []
    )


    found = False


    for item in cart:

        if item.get("id") == photo_id:

            item["quantity"] = (
                item.get(
                    "quantity",
                    1
                ) + 1
            )

            found = True

            break


    # -----------------------------------------------------
    # NEW ITEM
    # -----------------------------------------------------

    if not found:

        cart.append({

            "id":
                photo.get("id"),

            "filename":
                photo.get("filename"),

            "image_url":
                photo.get("image_url"),

            "flower_type":
                photo.get("flower_type"),

            "title_tamil":
                photo.get(
                    "title_tamil"
                ) or "",

            "title_english":
                photo.get(
                    "title_english"
                ) or "",

            "quantity":
                1

        })


    session["cart"] = cart

    session.modified = True


    return redirect(
        f"/home?lang={lang}"
    )


# =========================================================
# DECREASE CART
# =========================================================

@app.route(
    "/decrease-cart/<int:photo_id>"
)
def decrease_cart(photo_id):

    lang = request.args.get(
        "lang",
        "en"
    )


    cart = session.get(
        "cart",
        []
    )


    for item in cart:

        if item.get("id") == photo_id:

            quantity = item.get(
                "quantity",
                1
            )


            if quantity > 1:

                item["quantity"] = (
                    quantity - 1
                )

            else:

                cart.remove(
                    item
                )

            break


    session["cart"] = cart

    session.modified = True


    return redirect(
        f"/cart?lang={lang}"
    )


# =========================================================
# REMOVE CART ITEM
# =========================================================

@app.route(
    "/remove-from-cart/<int:photo_id>"
)
def remove_from_cart(photo_id):

    lang = request.args.get(
        "lang",
        "en"
    )


    cart = session.get(
        "cart",
        []
    )


    cart = [

        item

        for item in cart

        if item.get("id") != photo_id

    ]


    session["cart"] = cart

    session.modified = True


    return redirect(
        f"/cart?lang={lang}"
    )


# =========================================================
# CLEAR CART
# =========================================================

@app.route("/clear-cart")
def clear_cart():

    lang = request.args.get(
        "lang",
        "en"
    )


    session["cart"] = []

    session.modified = True


    return redirect(
        f"/cart?lang={lang}"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()


        password = request.form.get(
            "password",
            ""
        )


        if (
            username == "admin"
            and
            password == "admin123"
        ):

            session["admin_logged_in"] = True

            return redirect(
                "/admin/dashboard"
            )


        return render_template(

            "admin/login.html",

            error=
                "Invalid username or password."

        )


    return render_template(
        "admin/login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            "/admin"
        )


    supabase = get_supabase()


    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    try:

        result = (
            supabase
            .table("categories")
            .select(
                "id, name, name_tamil"
            )
            .order("id")
            .execute()
        )

        categories = result.data or []

    except Exception as error:

        print(
            "ADMIN CATEGORY ERROR:",
            error
        )

        categories = []


    # -----------------------------------------------------
    # PHOTOS
    # -----------------------------------------------------

    try:

        result = (
            supabase
            .table("photos")
            .select("*")
            .order(
                "uploaded_at",
                desc=True
            )
            .execute()
        )

        photos = result.data or []

    except Exception as error:

        print(
            "ADMIN PHOTO ERROR:",
            error
        )

        photos = []


    # -----------------------------------------------------
    # COUNTS
    # -----------------------------------------------------

    total_photos = len(
        photos
    )


    counts = {}


    for category in categories:

        category_name = category.get(
            "name"
        )


        counts[category_name] = sum(

            1

            for photo in photos

            if photo.get(
                "flower_type"
            )
            ==
            category_name

        )


    # -----------------------------------------------------
    # IMAGE URL
    # -----------------------------------------------------

    for photo in photos:

        if not photo.get(
            "image_url"
        ):

            photo["image_url"] = (
                get_supabase_image_url(

                    photo.get(
                        "flower_type"
                    ),

                    photo.get(
                        "filename"
                    )

                )
            )


    return render_template(

        "admin/dashboard.html",

        photos=photos,

        total_photos=
            total_photos,

        counts=counts,

        categories=categories

    )


# =========================================================
# ADMIN UPLOAD
# =========================================================

@app.route(
    "/admin/upload",
    methods=["POST"]
)
def admin_upload():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            "/admin"
        )


    flower_type = request.form.get(
        "flower_type",
        ""
    ).strip()


    title_tamil = request.form.get(
        "title_tamil",
        ""
    ).strip()


    title_english = request.form.get(
        "title_english",
        ""
    ).strip()


    supabase = get_supabase()


    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    try:

        result = (
            supabase
            .table("categories")
            .select(
                "id, name, name_tamil"
            )
            .execute()
        )

        categories = result.data or []

    except Exception as error:

        print(
            "UPLOAD CATEGORY ERROR:",
            error
        )

        return redirect(
            "/admin/dashboard"
        )


    valid_categories = [

        category.get("name")

        for category in categories

    ]


    if flower_type not in valid_categories:

        return redirect(
            "/admin/dashboard"
        )


    # -----------------------------------------------------
    # FILES
    # -----------------------------------------------------

    files = request.files.getlist(
        "photos"
    )


    if not files:

        return redirect(
            "/admin/dashboard"
        )


    # -----------------------------------------------------
    # UPLOAD
    # -----------------------------------------------------

    for file in files:

        if not file:
            continue


        if not file.filename:
            continue


        filename = secure_filename(
            file.filename
        )


        if not filename:
            continue


        folder = CATEGORY_FOLDERS.get(

            flower_type,

            flower_type

        )


        storage_path = (
            f"{folder}/{filename}"
        )


        try:

            file_bytes = file.read()


            # -------------------------------------------------
            # STORAGE UPLOAD
            # -------------------------------------------------

            supabase.storage.from_(
                SUPABASE_BUCKET
            ).upload(

                storage_path,

                file_bytes,

                {
                    "content-type":
                        file.content_type
                }

            )


            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            image_url = (

                f"{SUPABASE_URL}"

                f"/storage/v1/object/public/"

                f"{SUPABASE_BUCKET}/"

                f"{quote(folder, safe='')}/"

                f"{quote(filename, safe='')}"

            )


            # -------------------------------------------------
            # DATABASE
            # -------------------------------------------------

            supabase.table(
                "photos"
            ).insert({

                "filename":
                    filename,

                "image_url":
                    image_url,

                "flower_type":
                    flower_type,

                "title_tamil":
                    title_tamil,

                "title_english":
                    title_english

            }).execute()


            print(
                "UPLOAD SUCCESS:",
                storage_path
            )


        except Exception as error:

            print(
                "UPLOAD ERROR:",
                error
            )


    return redirect(
        "/admin/dashboard"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect("/")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )

