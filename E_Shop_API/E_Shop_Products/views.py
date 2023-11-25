from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from E_Shop_API.E_Shop_Products.models import Product, ProductImage
from E_Shop_API.E_Shop_Products.serializers import ProductSerializer


class ProductCreateView(APIView):
    """ Create Product """
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    @staticmethod
    def post(request):
        """ Create product """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            product_id = serializer.data['id']
            image = request.FILES.get('image')
            if image:
                product = Product.objects.get(id=product_id)
                ProductImage.objects.create(product=product, image=image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(APIView):
    """ Info about all product '/api/products/' """
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def get(request):
        """ Filer for Product queryset """
        queryset = Product.objects.all()
        if not request.user.is_staff:
            queryset = queryset.filter(count__gt=0)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductView(APIView):
    """ GET/PUT/PATCH/DELETE Product """
    permission_classes = [permissions.IsAdminUser]

    @staticmethod
    def get(request, pk):
        """ GET Method product/<int:pk>/ """
        product = Product.objects.get(pk=pk)
        if not request.user.is_staff and product.count == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @staticmethod
    def update_product(product, request):
        """ Update mixin """
        serializer = ProductSerializer(product, data=request.data, partial=True if request.method == 'PATCH' else False)
        if serializer.is_valid():
            serializer.save()
            # Process and save the uploaded image
            image = request.FILES.get('image')
            if image:
                product_image = ProductImage.objects.filter(product=product).first()
                if product_image:
                    product_image.image = image
                    product_image.save()
                else:
                    ProductImage.objects.create(product=product, image=image)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """ PUT Method product/<int:pk>/ """
        product = Product.objects.get(pk=pk)
        return self.update_product(product, request)

    def patch(self, request, pk):
        """ PATCH Method product/<int:pk>/ """
        product = Product.objects.get(pk=pk)
        return self.update_product(product, request)

    @staticmethod
    def delete(request, pk):
        """ DELETE Method product/<int:pk>/ """
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response({'message': 'Product is deleted'}, status=204)
