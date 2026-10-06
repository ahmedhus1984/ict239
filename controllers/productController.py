from flask import Blueprint, request, render_template
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
