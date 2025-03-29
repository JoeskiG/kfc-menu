import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

URL = "https://orderserv-kfc-apac-olo-api.yum.com/dev/v1/catalogs/afd3813afa364270bfd33f0a8d77252d/KFCAustraliaMenu-101-app-pickup"

session = requests.Session()
headers = requests.utils.default_headers()

headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_8_8; en-US) AppleWebKit/602.10 (KHTML, like Gecko) Chrome/49.0.2165.243 Safari/534",
    }
)


class SecretMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KFC Menu")
        self.root.state("zoomed")

        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(
            self.frame, orient="vertical", command=self.canvas.yview
        )
        self.scroll_frame = ttk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.fetch_menu()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def fetch_menu(self):
        try:
            response = session.get(URL, headers=headers)
            response.raise_for_status()
            data = response.json()

            secret_menu = next(
                (
                    cat
                    for cat in data["categories"][0]["categories"]
                    if cat["url"] == "secret-menu"
                ),
                None,
            )
            if not secret_menu:
                return

            for item in secret_menu.get("products", []):
                self.display_item(item)
        except requests.exceptions.RequestException as e:
            print("Error fetching data:", e)

    def display_item(self, item):
        frame = ttk.Frame(self.scroll_frame, padding=10)
        frame.pack(fill="x", expand=True)

        print("Name: " + item["name"])
        name_label = ttk.Label(frame, text=item["name"], font=("Arial", 14, "bold"))
        name_label.pack()

        if not item.get("items"):
            return

        main_item = item["items"][0]

        price = (
            next(
                (a["price"] for a in main_item.get("availability", []) if "price" in a),
                0,
            )
        ) / 100
        price_string = f"Price: ${price:.2f} AUD"
        print("Price: " + price_string)
        price_label = ttk.Label(frame, text=price_string, font=("Arial", 12))
        price_label.pack()

        if "imageName" in item:
            try:
                print("Image URL: " + item["imageName"])
                img_response = session.get(item["imageName"])
                img_response.raise_for_status()
                img_data = Image.open(BytesIO(img_response.content))
                img_data = img_data.resize((150, 150))
                img = ImageTk.PhotoImage(img_data)
                img_label = tk.Label(frame, image=img)
                img_label.image = img
                img_label.pack()
            except requests.exceptions.RequestException:
                pass

        if main_item.get("modgrpIds"):
            for modifier_group in main_item["modgrpIds"]:
                modifier_group_label_string = (
                    f"Modifier Group: {modifier_group.get('name', 'Unknown')}"
                )
                print(modifier_group_label_string)
                modifier_group_label = ttk.Label(
                    frame,
                    text=modifier_group_label_string,
                    font=("Arial", 11, "italic"),
                )
                modifier_group_label.pack()

                if modifier_group.get("modifiers"):
                    for modifier in modifier_group["modifiers"]:
                        modifier_label_string = (
                            f"  - Modifier: {modifier.get('name', 'Unknown')}"
                        )
                        print(modifier_label_string)
                        modifier_label = ttk.Label(
                            frame,
                            text=modifier_label_string,
                            font=("Arial", 10),
                        )
                        modifier_label.pack()

        print("---------------------------------------------------\n\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = SecretMenuApp(root)
    root.mainloop()
