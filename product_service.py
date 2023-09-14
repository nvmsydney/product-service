import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.sqlite')
db = SQLAlchemy(app)


class ProductService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0.0)


@app.route('/products', methods=['GET'])
def get_products():
    products = ProductService.query.all()
    product_list = [{"product_name": product.product_name, "price": product.price, "quantity": product.quantity} for
                    product in products]
    return jsonify({"products": product_list})


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = ProductService.query.get(product_id)
    if product:
        return jsonify(
            {"product": {"product_name": product.product_name, "price": product.price, "quantity": product.quantity}})
    else:
        return jsonify({"error": "Product not found"}), 404


@app.route('/products', methods=['POST'])
def add_product():
    data = request.json
    if "product_name" and "price" not in data:
        return jsonify({"error": "Product name and price are required"}), 400

    new_product = ProductService(product_name=data["product_name"], price=data["price"])

    db.session.add(new_product)
    db.session.commit()

    return jsonify({"success": "Product added successfully", "product_id": new_product.id}), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)