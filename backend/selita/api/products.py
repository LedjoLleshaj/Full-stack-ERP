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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# ======== PRODUCTS ========


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProducts(request):
    try:
        from django.db.models import Subquery, OuterRef
        
        # Optimized: Use Subquery to get inventory quantity in ONE query
        products = Product.objects.annotate(
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
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addProduct(request):
    try:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {"message": "Product added successfully!", "product_id": product.id},
                status=201,
            )
        return Response(serializer.errors, status=400)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
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
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProduct(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProductByName(request, name):
    try:
        product = Product.objects.get(name=name)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProductCategories(request):
    try:
        categories = Product_Categories.objects.all()
        serializer = ProductCategoriesSerializer(categories, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProductNames(request):
    try:
        names = Product_Names.objects.all()
        serializer = ProductNamesSerializer(names, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProductsByCategory(request, category):
    try:
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filterByCategories(request):
    # Get the 'categories' parameter from the query string
    categories = request.GET.get("categories", "")

    # If the 'categories' parameter is empty, return an empty list
    if not categories:
        products = Product.objects.all()
    else:
        # Split the comma-separated string into a list
        categories_list = categories.split(",")

        # Filter products whose category is in the list of categories
        products = Product.objects.filter(category__in=categories_list)

    product_serializer = ProductSerializer(products, many=True)

    for product in product_serializer.data:
        try:
            inventory = Inventory.objects.get(prod=product["id"])
            product["disponibility"] = inventory.quantity
        except ObjectDoesNotExist:
            product["disponibility"] = 0
    return Response(product_serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getProductByNames(request, name):
    name = Product.objects.filter(name=name)
    serializer = ProductSerializer(name, many=False)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def checkDisponibility(request, pk):
    try:
        product = Product.objects.get(id=pk)
        inventory = Inventory.objects.get(prod=product)
        serializer = InventorySerializer(inventory, many=False)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
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
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
