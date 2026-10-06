from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.product import Product
from models.review import Review




product = Blueprint('productController', __name__)


@product.route('/')
@product.route('/products')
def products():
    selected_category = request.args.get("category", "All Categories")

    if selected_category == "All Categories":
        all_products = Product.getAllProducts()
    else:
        all_products = Product.objects(category=selected_category)

    for p in all_products:
        p.avg_rating = Review.getAverageRating(p)
        p.review_count = Review.getReviewCount(p)
        p.newest_review = Review.getNewestReview(p)

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
    the_product = Product.getProduct(product_id)
    if the_product:
        the_product.avg_rating = Review.getAverageRating(the_product)
        the_product.review_count = Review.getReviewCount(the_product)
        the_product.all_reviews = list(Review.getProductReviews(the_product))
    return render_template('productDetail.html', panel="Product Detail", product=the_product)


@product.route('/manageProducts')
@login_required
def manage_products():
    if current_user.email != "admin@abc.com":
        flash("Admins only.", "warning")
        return redirect(url_for('productController.products'))

    all_products = list(Product.getAllProducts())
    categories = Product.objects().distinct("category")
    return render_template('manageProducts.html', panel="Admin Product Management",
                           all_products=all_products, categories=categories)


@product.route('/manageProducts/update/<product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    if current_user.email != "admin@abc.com":
        flash("Admins only.", "warning")
        return redirect(url_for('productController.products'))

    try:
        special_price = float(request.form.get('special_price'))
        usual_price = float(request.form.get('usual_price'))
        stock_qty = int(request.form.get('stock_qty'))
    except (TypeError, ValueError):
        flash("Invalid number entered.", "danger")
        return redirect(url_for('productController.manage_products'))

    description = request.form.get('description', '').strip()

    # Sanity checks
    if special_price <= 0:
        flash("Special price must be greater than 0.", "danger")
        return redirect(url_for('productController.manage_products'))
    if usual_price <= 0:
        flash("Usual price must be greater than 0.", "danger")
        return redirect(url_for('productController.manage_products'))
    if stock_qty < 0:
        flash("Stock cannot be negative.", "danger")
        return redirect(url_for('productController.manage_products'))
    if not description:
        flash("Description cannot be blank.", "danger")
        return redirect(url_for('productController.manage_products'))

    Product.updateProduct(product_id, special_price, usual_price, stock_qty, description)
    flash("Product updated.", "success")
    return redirect(url_for('productController.manage_products'))