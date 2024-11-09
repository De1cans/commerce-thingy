from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="postgresql+psycopg2://ecommerce_dev:123456@localhost:5432/jul_ecommerce"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model = Table 
class Product(db.Model):
    # define tablename 
    __tablename__ = "products"
    # define the primary key
    id = db.Column(db.Integer, primary_key=True)
    # more attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

# Schema for marshmallow model
class ProductSchema(ma.Schema):
    class Meta:
        # Fields to be serialised
        fields = ("id", "name", "description", "price", "stock")

# To handle multiple products
products_schema = ProductSchema(many=True)
# To handle a single product
product_schema = ProductSchema()

# CLI Commands
@app.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created")

@app.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@app.cli.command("seed")
def seed_db():
    # create a product object(instance)
    product1= Product(
        name ="Product 1",
        description ="Product 1 description",
        price =12.99,
        stock=15
    )
    product2 = Product()
    product2.name = "Product 2"
    product2.price = 149.99
    product2.stock = 25

    # add to session
    db.session.add(product1)
    db.session.add(product2)
    # commit
    db.session.commit()
    print("Tables seeded")

# get all products - /products - GET
# get a single product - /products/id - GET
# create a product - /products - POST
# update a product - /products/id - PUT, PATCH
# delete a product - /products/id - DELETE   

# CRUD for products
# R of CRUD - Read - GET method
@app.route("/products")
def get_products():
    stmt = db.select(Product) # SELECT * FROM products;
    products_list = db.session.scalars(stmt)
    data = products_schema.dump(products_list)
    return data

@app.route("/products/<int:product_id>")
def get_product(product_id):
    stmt = db.select(Product).filter_by(id=product_id) # SELECT * FROM products WHERE id=product_id
    product = db.session.scalar(stmt)
    if product:
        data = product_schema.dump(product)
        return data
    else:
        return {"message": f"Product with id {product_id} does not exist"}, 404

@app.route("/products", methods=["POST"])
def create_product():
    body_data = request.get_json()
    new_product = Product(
        name=body_data.get("name"),
        description=body_data.get("descrition"),
        price=body_data.get("price"),
        stock=body_data.get("stock")
    )
    db.session.add(new_product)
    db.session.commit()
    return product_schema.dump(new_product), 201

# D of CRUD - DELETE - DELETE method 
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    # find the product with that id from the database
    stmt = db.select(Product).where(Product.id==product_id)
    #Where id=product_id;
    product = db.session.scalar(stmt)
    # if the products exists
    if product:
        # delete the product
        db.session.delete(product)
        db.session.commit()
        # respond with a message saying the product has been deleted
        return {"message": f"Product '{product.name}' deleted successfully"}
    #else 
    else:
        # respond with a message saying product with that id does not exist 
        return {"message": f"Product with id {product_id} does not exist"}, 404