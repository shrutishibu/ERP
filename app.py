from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

FILE_NAME = "inventory.csv"

def load_inventory():
    """Load inventory from CSV."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"])
    with open(FILE_NAME, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def save_inventory(inventory):
    """Save inventory to CSV."""
    with open(FILE_NAME, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Product ID", "Product Name", "Category", "Price", "Stock", "Total Sales"])
        writer.writeheader()
        writer.writerows(inventory)

@app.route('/')
def home():
    inventory = load_inventory()
    return render_template("index.html", inventory=inventory)

@app.route('/add_product', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        inventory = load_inventory()
        product_id = request.form["product_id"]
        if any(item["Product ID"] == product_id for item in inventory):
            return "Error: Product ID already exists."
        
        inventory.append({
            "Product ID": product_id,
            "Product Name": request.form["product_name"],
            "Category": request.form["category"],
            "Price": int(request.form["price"]),
            "Stock": int(request.form["stock"]),
            "Total Sales": "0"
        })
        save_inventory(inventory)
        return redirect(url_for("home"))
    
    return render_template("add_product.html")

@app.route('/update_product/<product_id>', methods=["GET", "POST"])
def update_product(product_id):
    inventory = load_inventory()
    product = next((item for item in inventory if item["Product ID"] == product_id), None)
    
    if not product:
        return "Error: Product not found."

    if request.method == "POST":
        product["Product Name"] = request.form["product_name"]
        product["Category"] = request.form["category"]
        product["Price"] = request.form["price"]
        product["Stock"] = request.form["stock"]
        save_inventory(inventory)
        return redirect(url_for("home"))

    return render_template("update_product.html", product=product)

@app.route('/delete_product/<product_id>', methods=["POST"])
def delete_product(product_id):
    inventory = load_inventory()
    inventory = [item for item in inventory if item["Product ID"] != product_id]
    save_inventory(inventory)
    return redirect(url_for("home"))

@app.route('/record_sale/<product_id>', methods=["GET", "POST"])
def record_sale(product_id):
    inventory = load_inventory()
    product = next((item for item in inventory if item["Product ID"] == product_id), None)
    
    if not product:
        return "Error: Product not found."

    if request.method == "POST":
        quantity = int(request.form["quantity"])
        stock = int(product["Stock"])
        
        if quantity > stock:
            return "Error: Insufficient stock."

        product["Stock"] = str(stock - quantity)
        product["Total Sales"] = str(int(product["Total Sales"]) + quantity)
        save_inventory(inventory)
        return redirect(url_for("home"))

    return render_template("record_sale.html", product=product)

@app.route('/recommend_restock', methods=["GET", "POST"])
def recommend_restock():
    inventory = load_inventory()
    recommendations = []

    if request.method == "GET":
        threshold = 10
        recommendations = [
            {"name": item["Product ID"], "stock": int(item["Stock"]), "restock_needed": threshold - int(item["Stock"])}
            for item in inventory if int(item["Stock"]) < threshold
        ]

    return render_template("recommend_restock.html", recommendations=recommendations)

@app.route('/restock_product/<product_id>', methods=["POST"])
def restock_product(product_id):
    inventory = load_inventory()
    product = next((item for item in inventory if item["Product ID"] == product_id), None)

    if not product:
        return "Error: Product not found."

    product["Stock"] = str(int(product["Stock"]) + 10)  # Add 10 to stock
    save_inventory(inventory)
    return redirect(url_for("recommend_restock"))


if __name__ == "__main__":
    app.run(debug=True)
