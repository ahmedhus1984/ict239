from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from models.cart import Cart
from models.orders import Order
from models.review import Review
from models.product import Product

orders = Blueprint('ordersController', __name__)


@orders.route('/checkout', methods=['POST'])
@login_required
def checkout():
    if current_user.email == "admin@abc.com":
        flash("Admins are not allowed to purchase items.", "warning")
        return redirect(url_for('productController.products'))

    cart = Cart.getCart(current_user)

    if not cart.items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for('cartController.cart_view'))

    # Validate stock
    for item in cart.items:
        if not item.product:
            continue
        if item.qty > item.product.stock_qty:
            flash(f"{item.product.name} cannot be fulfilled (only {item.product.stock_qty} left).", "danger")
            return redirect(url_for('cartController.cart_view'))

    # Create order
    order = Order.createOrder(current_user, cart)

    # Decrement stock
    for item in cart.items:
        if item.product:
            item.product.stock_qty -= item.qty
            item.product.save()

    # Empty the cart
    cart.items = []
    cart.save()

    flash("Order successfully placed!", "success")
    return redirect(url_for('ordersController.orders_page'))


@orders.route('/orders')
@login_required
def orders_page():
    if current_user.email == "admin@abc.com":
        flash("Admins do not have orders.", "warning")
        return redirect(url_for('productController.products'))

    user_orders = Order.getUserOrders(current_user)
        # build a map: product_id -> existing review by this user
    reviews_map = {}
    for order in user_orders:
        for item in order.items:
            if item.product:
                key = str(item.product.id)
                if key not in reviews_map:
                    reviews_map[key] = Review.getReview(current_user, item.product)

    return render_template('orders.html', panel="Your Orders",
                           orders=user_orders, reviews_map=reviews_map)


@orders.route('/orders/review', methods=['POST'])
@login_required
def submit_review():
    if current_user.email == "admin@abc.com":
        flash("Admins cannot submit reviews.", "warning")
        return redirect(url_for('productController.products'))

    product_id = request.form.get('product_id')
    rating = int(request.form.get('rating'))
    text = request.form.get('review')

    the_product = Product.getProduct(product_id)
    if the_product is None:
        flash("Product not found.", "danger")
        return redirect(url_for('ordersController.orders_page'))

    existing = Review.getReview(current_user, the_product)
    Review.addOrUpdate(current_user, the_product, rating, text)

    if existing:
        flash("Review updated.", "success")
    else:
        flash("Review submitted.", "success")

    return redirect(url_for('ordersController.orders_page'))