from flask import Flask, jsonify, request

app = Flask(__name__)

products = [
    {"id": 1, "product_name": "Coconut Water", "price": 10.99, "quantity": 20},
    {"id": 2, "product_name": "Xylitol Gum", "price": 4.99, "quantity": 12},
    {"id": 3, "product_name": "Rotisserie Chicken", "price": 6.99, "quantity": 7}
]


@app.route('/products', methods=['GET'])
def get_products():
    return jsonify({"products": products})


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((product for product in products if product["id"] == product_id), None)
    if product:
        return jsonify({"product": product})
    else:
        return jsonify({"error": "Product not found."}), 404


@app.route('/products', methods=['POST'])
def add_product():
    new_product = {
        "id": len(products) + 1,
        "product_name": request.json.get('product_name'),
        "price": request.json.get('price'),
        "quantity": request.json.get('quantity')
    }
    products.append(new_product)
    return jsonify({"message": "Product added", "product": new_product}), 201


if __name__ == '__main__':
    app.run(debug=True)
