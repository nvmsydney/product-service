import os

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cart.sqlite')
db = SQLAlchemy(app)

PRODUCT_SERVICE_URL = "http://127.0.0.1:5000"


class Cart(db.Model):
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    total_price = db.Column(db.Float, default=0.0)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('cart.user_id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1)


@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart = Cart.query.get(user_id)
    if not cart:
        return jsonify({"error": "Cart not found for user."}), 404

    items = []
    total_price = 0

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    for item in cart_items:
        product_details = requests.get(f'{PRODUCT_SERVICE_URL}/products/{item.product_id}').json().get("product")
        if product_details:
            price = product_details["price"]
            total_price += price * item.quantity
            items.append({
                "product_id": item.product_id,
                "product_name": product_details["product_name"],
                "quantity": item.quantity,
                "price": price
            })

    return jsonify({"items": items, "total_price": total_price})


@app.route('/cart/<int:user_id>/add/<int:product_id>', methods=['POST'])
def add_to_cart(user_id, product_id):
    data = request.json
    desired_quantity = data.get("quantity", 1)

    response = requests.get(f'{PRODUCT_SERVICE_URL}/products/{product_id}')
    if response.status_code != 200:
        return jsonify({"error": "Product not found."}), 404

    product_data = response.json().get("product")
    product_name = product_data.get("product_name")
    available_quantity = product_data.get("quantity")
    price = product_data.get("price")

    if available_quantity < desired_quantity:
        return jsonify({"error": "Not enough stock available."}), 400

    cart = Cart.query.get(user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=desired_quantity)
        cart.total_price += price * desired_quantity
        db.session.add(cart_item)
    else:
        cart_item.quantity += desired_quantity
        cart.total_price += price * desired_quantity

    db.session.commit()
    return jsonify({"message": f"Added {desired_quantity} of {product_name} to the cart."})


@app.route('/cart/<int:user_id>/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(user_id, product_id):
    data = request.json
    remove_quantity = data.get("quantity", 1)

    cart = Cart.query.get(user_id)
    if not cart:
        return jsonify({"error": "Cart not found for user."}), 404

    cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        return jsonify({"error": "Product not found in cart."}), 404

    product_details = requests.get(f'{PRODUCT_SERVICE_URL}/products/{product_id}').json().get("product")
    price = product_details["price"]

    if cart_item.quantity > remove_quantity:
        cart_item.quantity -= remove_quantity
        cart.total_price -= price * remove_quantity
    else:
        cart.total_price -= price * cart_item.quantity
        db.session.delete(cart_item)

    db.session.commit()

    return jsonify({"message": f"Removed {remove_quantity} of product {product_id} from the cart."})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
