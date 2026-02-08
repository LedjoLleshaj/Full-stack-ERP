from rest_framework.response import Response
from ..models import Product, Product_Categories, Product_Names, Inventory
from rest_framework.decorators import api_view, permission_classes
from ..serializers import (
    ProductSerializer,
    ProductCategoriesSerializer,
    ProductNamesSerializer,
    InventorySerializer,
)
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from selita.utils.responses import api_error_handler, not_found_response


# ======== PRODUCTS ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProducts(request):
    from django.db.models import Subquery, OuterRef
    
    # Optimized: Use Subquery to get inventory quantity in ONE query
    # Only return active products (soft delete filter)
    products = Product.objects.filter(is_active=True).annotate(
        disponibility=Subquery(
            Inventory.objects.filter(prod=OuterRef('pk')).values('quantity')[:1]
        )
    )
    
    # Build response with disponibility already attached
    results = []
    for product in products:
        results.append({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": float(product.price) if product.price else None,
            "description": product.description,
            "disponibility": float(product.disponibility) if product.disponibility else 0,
        })
    
    return Response(results)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_error_handler
def addProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(
            {"message": "Product added successfully!", "product_id": product.id},
            status=201,
        )
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@api_error_handler
def updatePrice(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product price updated successfully!"}, status=200
            )
        return Response(serializer.errors, status=400)
    except ObjectDoesNotExist:
        return not_found_response("Product")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Product")


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@api_error_handler
def updateProduct(request, pk):
    """Full product update (name, category, price, description)"""
    try:
        product = Product.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Product")
    
    data = request.data
    
    # Check if new name conflicts with existing product (if name is being changed)
    new_name = data.get("name", "").strip()
    if new_name and new_name != product.name:
        if Product.objects.filter(name__iexact=new_name).exclude(id=pk).exists():
            return Response(
                {"error": f"A product with name '{new_name}' already exists"},
                status=400
            )
        product.name = new_name
    
    # Update other fields
    if "category" in data:
        product.category = data["category"]
    if "price" in data:
        product.price = data["price"]
    if "description" in data:
        product.description = data["description"]
    
    product.save()
    
    # Also update inventory if product name changed (for consistency)
    if new_name:
        Inventory.objects.filter(prod=product).update(prod=product)
    
    serializer = ProductSerializer(product, many=False)
    return Response({
        "message": "Product updated successfully",
        "product": serializer.data
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@api_error_handler
def deleteProduct(request, pk):
    """Soft delete product (deactivate) even if sales/history exists"""
    from ..models import Sales, Restock
    
    try:
        product = Product.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Product")
    # Soft delete - set is_active to False instead of deleting
    # We do NOT check for sales/restocks/inventory because soft delete allows keeping history
    product.is_active = False
    product.save()
    
    # Also set inventory to 0 as the product is now "gone"
    Inventory.objects.filter(prod=product).update(quantity=0)
    
    return Response({"message": "Product deactivated successfully"})
    



@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductByName(request, name):
    try:
        product = Product.objects.get(name=name)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Product")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductCategories(request):
    # Filter out categories that contain ONLY inactive products
    # 1. Categories with inactive products
    inactive_cats = set(Product.objects.filter(is_active=False).values_list('category', flat=True))
    # 2. Categories with active products
    active_cats = set(Product.objects.filter(is_active=True).values_list('category', flat=True))
    
    # Categories to hide: Used by inactive, but NOT used by active
    cats_to_hide = inactive_cats - active_cats
    
    categories = Product_Categories.objects.exclude(category_name__in=cats_to_hide)
    serializer = ProductCategoriesSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductNames(request):
    # Get names of inactive products to exclude from suggestions
    inactive_product_names = Product.objects.filter(is_active=False).values_list('name', flat=True)
    
    # Exclude these names from suggestions
    names = Product_Names.objects.exclude(product_name__in=inactive_product_names)
    serializer = ProductNamesSerializer(names, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductsByCategory(request, category):
    products = Product.objects.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def filterByCategories(request):
    # Get the 'categories' parameter from the query string
    categories = request.GET.get("categories", "")
    from django.db.models import Subquery, OuterRef

    # If the 'categories' parameter is empty, return all active products
    if not categories:
        products = Product.objects.filter(is_active=True)
    else:
        # Split the comma-separated string into a list
        categories_list = categories.split(",")

        # Filter active products whose category is in the list of categories
        products = Product.objects.filter(is_active=True, category__in=categories_list)
    
    # Optimized: Use Subquery to get inventory quantity in ONE query
    products = products.annotate(
        disponibility=Subquery(
            Inventory.objects.filter(prod=OuterRef('pk')).values('quantity')[:1]
        )
    )
    
    # Build response with disponibility already attached
    results = []
    for product in products:
        results.append({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": float(product.price) if product.price else None,
            "description": product.description,
            "disponibility": float(product.disponibility) if product.disponibility else 0,
        })
    
    return Response(results)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductByNames(request, name):
    name = Product.objects.filter(name=name)
    serializer = ProductSerializer(name, many=False)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def checkDisponibility(request, pk):
    try:
        product = Product.objects.get(id=pk)
        inventory = Inventory.objects.get(prod=product)
        serializer = InventorySerializer(inventory, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return not_found_response("Product")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_error_handler
def addProductCategory(request):
    """Create a new product category or return existing one"""
    category_name = request.data.get("category_name", "").strip()
    
    if not category_name:
        return Response(
            {"error": "Category name is required"},
            status=400
        )
    
    # Check if category already exists (case-insensitive)
    existing = Product_Categories.objects.filter(category_name__iexact=category_name).first()
    if existing:
        serializer = ProductCategoriesSerializer(existing)
        return Response({
            "message": "Category already exists",
            "category": serializer.data,
            "created": False
        })
    
    # Create new category
    category = Product_Categories.objects.create(category_name=category_name)
    serializer = ProductCategoriesSerializer(category)
    return Response({
        "message": "Category created successfully",
        "category": serializer.data,
        "created": True
    }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@api_error_handler
def addProductName(request):
    """Create a new product name linked to a category"""
    product_name = request.data.get("product_name", "").strip()
    category_name = request.data.get("category_name", "").strip()
    category_id = request.data.get("category_id")
    
    if not product_name:
        return Response(
            {"error": "Product name is required"},
            status=400
        )
    
    # Check if product name already exists (case-insensitive)
    existing = Product_Names.objects.filter(product_name__iexact=product_name).first()
    if existing:
        serializer = ProductNamesSerializer(existing)
        return Response({
            "message": "Product name already exists",
            "product_name": serializer.data,
            "created": False
        })
    
    # Get or create category
    category = None
    if category_id:
        try:
            category = Product_Categories.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return not_found_response("Category")
    elif category_name:
        # Check if category exists (case-insensitive)
        category = Product_Categories.objects.filter(category_name__iexact=category_name).first()
        if not category:
            # Create new category
            category = Product_Categories.objects.create(category_name=category_name)
    else:
        return Response(
            {"error": "Either category_id or category_name is required"},
            status=400
        )
    
    # Create new product name
    product_name_obj = Product_Names.objects.create(
        product_name=product_name,
        category=category
    )
    serializer = ProductNamesSerializer(product_name_obj)
    return Response({
        "message": "Product name created successfully",
        "product_name": serializer.data,
        "category": ProductCategoriesSerializer(category).data,
        "created": True
    }, status=201)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@api_error_handler
def updateProductCategory(request, pk):
    """Update a product category"""
    try:
        category = Product_Categories.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Category")
    
    category_name = request.data.get("category_name", "").strip()
    if not category_name:
        return Response({"error": "Category name is required"}, status=400)
    
    # Check for duplicate name (case-insensitive, exclude self)
    if Product_Categories.objects.filter(category_name__iexact=category_name).exclude(id=pk).exists():
        return Response({"error": f"A category with name '{category_name}' already exists"}, status=400)
    
    old_name = category.category_name
    category.category_name = category_name
    category.save()
    
    # Also update any products that use this category name
    Product.objects.filter(category__iexact=old_name).update(category=category_name)
    
    serializer = ProductCategoriesSerializer(category)
    return Response({
        "message": "Category updated successfully",
        "category": serializer.data
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@api_error_handler
def deleteProductCategory(request, pk):
    """Delete a product category - reassign products to use their name as category"""
    try:
        category = Product_Categories.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Category")
    
    category_name = category.category_name
    
    # Update Product_Names linked to this category - reassign to "Uncategorized"
    # First, get or create an "Uncategorized" category
    uncategorized, created = Product_Categories.objects.get_or_create(
        category_name="Pa kategori",
        defaults={"category_name": "Pa kategori"}
    )
    Product_Names.objects.filter(category=category).update(category=uncategorized)
    
    # Update products using this category - set category to product name
    for product in Product.objects.filter(category__iexact=category_name):
        product.category = product.name
        product.save()
    
    category.delete()
    return Response({
        "message": "Category deleted successfully",
        "products_updated": Product.objects.filter(category__iexact=category_name).count()
    })


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@api_error_handler
def updateProductName(request, pk):
    """Update a product name"""
    try:
        product_name_obj = Product_Names.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Product name")
    
    new_name = request.data.get("product_name", "").strip()
    category_id = request.data.get("category_id")
    
    if new_name:
        # Check for duplicate name (case-insensitive, exclude self)
        if Product_Names.objects.filter(product_name__iexact=new_name).exclude(id=pk).exists():
            return Response({"error": f"A product name '{new_name}' already exists"}, status=400)
        product_name_obj.product_name = new_name
    
    if category_id:
        try:
            category = Product_Categories.objects.get(id=category_id)
            product_name_obj.category = category
        except ObjectDoesNotExist:
            return not_found_response("Category")
    
    product_name_obj.save()
    serializer = ProductNamesSerializer(product_name_obj)
    return Response({
        "message": "Product name updated successfully",
        "product_name": serializer.data
    })


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@api_error_handler
def deleteProductName(request, pk):
    """Delete a product name - can be deleted safely as it's only a suggestion list"""
    try:
        product_name_obj = Product_Names.objects.get(id=pk)
    except ObjectDoesNotExist:
        return not_found_response("Product name")
    
    product_name_obj.delete()
    return Response({"message": "Product name deleted successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@api_error_handler
def getProductHistory(request, pk):
    """
    Get product history including:
    - Last 10 sales
    - Last 10 restocks
    - Price history for chart (adjustable time range: 1-12 months)
    """
    from ..models import Sales, Restock
    from datetime import date, timedelta
    
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)
        product_data = serializer.data
        
        # Get disponibility
        try:
            inventory = Inventory.objects.get(prod=product)
            product_data["disponibility"] = inventory.quantity
        except ObjectDoesNotExist:
            product_data["disponibility"] = 0
        
        # Get time range from query params (default 3 months)
        months = int(request.query_params.get("months", 3))
        months = min(max(months, 1), 12)  # Clamp between 1 and 12
        start_date = date.today() - timedelta(days=months * 30)
        
        # Get last 10 sales for this product
        recent_sales = Sales.objects.filter(
            prod=product
        ).select_related('transaction', 'transaction__client').order_by('-sale_date')[:10]
        
        sales_list = []
        for sale in recent_sales:
            client = sale.transaction.client if sale.transaction else None
            client_name = f"{client.firstname} {client.lastname}" if client else "N/A"
            sales_list.append({
                "id": sale.id,
                "date": sale.sale_date.date().isoformat(),
                "price": float(sale.prod_price),
                "quantity": sale.quantity,
                "currency": sale.transaction.currency if sale.transaction else "EUR",
                "client_name": client_name,
                "transaction_id": sale.transaction.id if sale.transaction else None,
                "status": sale.transaction.status if sale.transaction else "PENDING"
            })
        
        # Get last 10 restocks for this product
        recent_restocks = Restock.objects.filter(
            prod=product
        ).select_related('transaction', 'transaction__supplier').order_by('-restock_date')[:10]
        
        restocks_list = []
        for restock in recent_restocks:
            supplier = restock.transaction.supplier if restock.transaction else None
            supplier_name = f"{supplier.firstname} {supplier.lastname}" if supplier else "N/A"
            restocks_list.append({
                "id": restock.id,
                "date": restock.restock_date.date().isoformat(),
                "price": float(restock.restock_price),
                "quantity": restock.quantity,
                "currency": restock.transaction.currency if restock.transaction else "EUR",
                "supplier_name": supplier_name
            })
        
        # Get price history for chart (within time range)
        # Sales prices
        sales_in_range = Sales.objects.filter(
            prod=product,
            sale_date__date__gte=start_date
        ).select_related('transaction').order_by('sale_date')
        
        sale_prices = []
        for sale in sales_in_range:
            sale_prices.append({
                "date": sale.sale_date.date().isoformat(),
                "price": float(sale.prod_price),
                "currency": sale.transaction.currency if sale.transaction else "EUR"
            })
        
        # Restock prices
        restocks_in_range = Restock.objects.filter(
            prod=product,
            restock_date__date__gte=start_date
        ).select_related('transaction').order_by('restock_date')
        
        restock_prices = []
        for restock in restocks_in_range:
            restock_prices.append({
                "date": restock.restock_date.date().isoformat(),
                "price": float(restock.restock_price),
                "currency": restock.transaction.currency if restock.transaction else "EUR"
            })
        
        return Response({
            "product": product_data,
            "recent_sales": sales_list,
            "recent_restocks": restocks_list,
            "price_history": {
                "sale_prices": sale_prices,
                "restock_prices": restock_prices
            }
        })
        
    except ObjectDoesNotExist:
        return not_found_response("Product")
