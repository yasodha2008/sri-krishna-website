from database import get_supabase
from urllib.parse import quote


SUPABASE_URL = "https://qajajtijyhnabknjhwvk.supabase.co"
BUCKET = "project-images"


# =========================================================
# STORAGE FOLDER → DATABASE CATEGORY
# =========================================================

CATEGORIES = {

    "bouquet":
        {
            "english": "Bouquet",
            "tamil": "பூங்கொத்து"
        },

    "crown":
        {
            "english": "Crown",
            "tamil": "கிரீடம்"
        },

    "hair-decoration":
        {
            "english": "Hair Decoration",
            "tamil": "முடி அலங்காரம்"
        },

    "hall-decoration":
        {
            "english": "Hall Decoration",
            "tamil": "மண்டப அலங்காரம்"
        },

    "temple-sculpture-decoration":
        {
            "english": "Temple Sculpture Decoration",
            "tamil": "கோவில் சிலை அலங்காரம்"
        },

    "flower-kolams":
        {
            "english": "Flower Kolams",
            "tamil": "மலர் கோலம்"
        },

    "large-garlands":
        {
            "english": "Large Garlands",
            "tamil": "பெரிய மாலைகள்"
        },

    "money-garlands":
        {
            "english": "Money Garlands",
            "tamil": "பண மாலைகள்"
        },

    "wedding-garlands":
        {
            "english": "Wedding Garlands",
            "tamil": "திருமண மாலைகள்"
        },

    "stage-decorations":
        {
            "english": "Stage Decorations",
            "tamil": "மேடை அலங்காரம்"
        }
}


# =========================================================
# CREATE PUBLIC IMAGE URL
# =========================================================

def create_image_url(folder, filename):

    return (
        f"{SUPABASE_URL}/storage/v1/object/public/"
        f"{BUCKET}/"
        f"{quote(folder, safe='')}/"
        f"{quote(filename, safe='')}"
    )


# =========================================================
# SUPABASE
# =========================================================

supabase = get_supabase()


print("\n======================================")
print("SRI KRISHNA FLOWER SHOP")
print("BULK PHOTO IMPORT")
print("======================================")


# =========================================================
# PROCESS ALL FOLDERS
# =========================================================

for folder, category in CATEGORIES.items():

    print("\n--------------------------------------")
    print("FOLDER:", folder)
    print("CATEGORY:", category["english"])
    print("--------------------------------------")


    try:

        files = (
            supabase
            .storage
            .from_(BUCKET)
            .list(
                folder,
                {
                    "limit": 1000
                }
            )
        )


        if not files:

            print("No files found.")
            continue


        print("Files found:", len(files))


        inserted = 0
        skipped = 0


        for file in files:

            filename = file.get("name")


            if not filename:

                continue


            # Ignore folders
            if file.get("id") is None and file.get("metadata") is None:

                # Some Supabase responses use id=None for folders.
                # We only want actual image files.
                if "." not in filename:

                    continue


            # =================================================
            # IMAGE URL
            # =================================================

            image_url = create_image_url(
                folder,
                filename
            )


            # =================================================
            # CHECK DUPLICATE
            # =================================================

            existing = (
                supabase
                .table("photos")
                .select("id")
                .eq(
                    "filename",
                    filename
                )
                .eq(
                    "image_url",
                    image_url
                )
                .execute()
            )


            if existing.data:

                print(
                    "SKIPPED:",
                    filename
                )

                skipped += 1

                continue


            # =================================================
            # INSERT DATABASE RECORD
            # =================================================

            supabase.table("photos").insert({

                "filename":
                    filename,

                "image_url":
                    image_url,

                "flower_type":
                    category["english"],

                "title_english":
                    category["english"],

                "title_tamil":
                    category["tamil"]

            }).execute()


            print(
                "INSERTED:",
                filename
            )

            inserted += 1


        print(
            f"Inserted: {inserted} | "
            f"Skipped: {skipped}"
        )


    except Exception as error:

        print(
            "ERROR:",
            folder
        )

        print(error)


# =========================================================
# FINISHED
# =========================================================

print("\n======================================")
print("BULK IMPORT COMPLETED")
print("======================================")