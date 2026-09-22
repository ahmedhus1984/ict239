from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.product import Product

product = Blueprint('productController', __name__)


@product.route('/')
@product.route('/products')
def products():
    selected_category = request.args.get("category", "All Categories")

    if selected_category == "All Categories":
        all_products = Product.getAllProducts()
    else:
        all_products = Product.objects(category=selected_category)

    categories = Product.objects().distinct("category")

    return render_template(
        'products.html',
        panel="Products",
        all_products=all_products,
        categories=categories,
        selected_category=selected_category
    )


@product.route("/viewProductDetail/<product_id>")
def viewProductDetail(product_id):
    the_product = Product.getProduct(product_id=product_id)
    return render_template('productDetail.html', panel="Product Detail", product=the_product)

@product.route("/cart")
@login_required
def cart():
    if current_user.email == "admin@abc.com":
        flash("Admins are not allowed to purchase items.", "warning")
        return redirect(url_for('productController.products'))
    return redirect(url_for('changeAvatar'))  # or wherever your cart page lives