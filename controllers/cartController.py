from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.cart import Cart
from models.product import Product

cart = Blueprint('cartController', __name__)


@cart.route('/cart')
@login_required
def cart_view():
    if current_user.email == "admin@abc.com":
        flash("Admins are not allowed to purchase items.", "warning")
        return redirect(url_for('productController.products'))

    the_cart = Cart.getCart(current_user)
    return render_template('cart.html', panel="Your Cart", cart=the_cart)


@cart.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    if current_user.email == "admin@abc.com":
        flash("Admins are not allowed to purchase items.", "warning")
        return redirect(url_for('productController.products'))

    product_id = request.form.get('product_id')
    qty = int(request.form.get('qty', 1))

    the_product = Product.getProduct(product_id)
    if the_product is None:
        flash("Product not found.", "danger")
        return redirect(url_for('productController.products'))

    Cart.addItem(current_user, the_product, qty)
    flash(f"Added {the_product.name} to cart.", "success")
    return redirect(url_for('cartController.cart_view'))


@cart.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    if current_user.email == "admin@abc.com":
        flash("Admins are not allowed to purchase items.", "warning")
        return redirect(url_for('productController.products'))

    product_id = request.form.get('product_id')
    qty = int(request.form.get('qty', 1))

    Cart.updateQty(current_user, product_id, qty)
    return redirect(url_for('cartController.cart_view'))


@cart.route('/cart/remove', methods=['POST'])
@login_required
def remove_from_cart():
    if current_user.email == "admin@abc.com":
        flash("Admins are not allowed to purchase items.", "warning")
        return redirect(url_for('productController.products'))

    product_id = request.form.get('product_id')
    Cart.removeItem(current_user, product_id)
    return redirect(url_for('cartController.cart_view'))