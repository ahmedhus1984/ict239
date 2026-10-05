from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models.cart import Cart
from models.orders import Order

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
    return render_template('orders.html', panel="Your Orders", orders=user_orders)