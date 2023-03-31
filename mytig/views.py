import requests
from mytig.models import Lot
from mytig.models import Sale
from rest_framework.views import APIView
from rest_framework.response import Response
from mytig.config import baseUrl
from mytig.models import InfoProduct
from mytig.serializers import InfoProductSerializer
from rest_framework import status
from django.http import Http404, JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from mytig.models import ProduitEnPromotion, AvailableProduct
from mytig.serializers import ProduitEnPromotionSerializer, AvailableProductSerializer
from django.http import HttpResponseNotFound
from django.shortcuts import render

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

class InfoProductList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        products = InfoProduct.objects.all()
        serializer = InfoProductSerializer(products, many=True)
        return Response(serializer.data)


class InfoProductDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, tig_id, format=None):
        try:
            product = InfoProduct.objects.get(tig_id=tig_id)
            serializer = InfoProductSerializer(product)
            return Response(serializer.data)
        except InfoProduct.DoesNotExist:
            raise Http404

class UpdateProductStock(APIView):
    def patch(self, request, tig_id):
        try:
            product = InfoProduct.objects.get(tig_id=tig_id)
        except InfoProduct.DoesNotExist:
            return Response({"error": f"Product {tig_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantityInStock = request.data["quantityInStock"]
            new_stock = product.quantityInStock + int(quantityInStock)
            if new_stock < 0:
                return Response({"error": "Stock cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)

            product.quantityInStock = new_stock
            product.save()
            serializer = InfoProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except KeyError:
            return Response({"error": "Missing parameter 'quantityInStock'"}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError:
            return Response({"error": "Invalid parameter 'quantityInStock'"}, status=status.HTTP_400_BAD_REQUEST)

#Modification de UpdatePorudctStock pour la partie 3, quand le front sera fini il faudra bien enlever les ocmmentaires 

'''
class UpdateProductStock(APIView):
    permission_classes = (IsAuthenticated,)
    def patch(self, request, tig_id):
        try:
            product = InfoProduct.objects.get(tig_id=tig_id)
        except InfoProduct.DoesNotExist:
            return Response({"error": f"Product {tig_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantityInStock = request.data["quantityInStock"]
            stock_change_price = request.data.get("stockChangePrice", 0)
            stock_change_type = request.data.get("stockChangeType", "add")

            if stock_change_type not in ["add", "remove_sell", "remove_perished"]:
                return Response({"error": "Invalid stock change type"}, status=status.HTTP_400_BAD_REQUEST)

            if stock_change_type == "add":
                if stock_change_price <= 0:
                    return Response({"error": "Invalid stock change price"}, status=status.HTTP_400_BAD_REQUEST)
                new_stock_value = product.quantityInStock + int(quantityInStock)
                new_stock_cost = product.stock_cost + (stock_change_price * int(quantityInStock))
            elif stock_change_type == "remove_sell":
                new_stock_value = product.quantityInStock - int(quantityInStock)
                new_stock_cost = product.stock_cost
            else: # stock_change_type == "remove_perished"
                new_stock_value = product.quantityInStock - int(quantityInStock)
                new_stock_cost = product.stock_cost

            if new_stock_value < 0:
                return Response({"error": "Stock cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)

            product.quantityInStock = new_stock_value
            product.stock_cost = new_stock_cost
            product.save()
            serializer = InfoProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except KeyError:
            return Response({"error": "Missing parameter 'quantityInStock'"}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError:
            return Response({"error": "Invalid parameter 'quantityInStock'"}, status=status.HTTP_400_BAD_REQUEST)

'''

class UpdateProductSalePercentage(APIView):
    def put(self, request, tig_id, format=None):
        try:
            product_data = request.data
            sale_percentage = product_data.get('discount')

            if sale_percentage is not None:
                # Récupérez le produit de la base de données
                try:
                    product = InfoProduct.objects.get(tig_id=tig_id)
                except InfoProduct.DoesNotExist:
                    return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

                # Mettez à jour les données de promotion du produit
                if 0 <= float(sale_percentage) <= 100:
                    product.sale_percentage = float(sale_percentage)
                    product.price_on_sale = product.price * (1 - float(sale_percentage) / 100)
                    product.sale = True
                    product.save()
                else:
                    return Response({'error': 'Invalid sale percentage'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = InfoProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            raise Http404



class ProductsByCategory(APIView):

    def get(self, request, category, format=None):
        if category not in ["0", "1", "2"]:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        products = InfoProduct.objects.filter(category=category)
        serializer = InfoProductSerializer(products, many=True)
        return Response(serializer.data)

class UpdateMultipleProductStocks(APIView):
    def put(self, request, format=None):
        products_data = request.data

        for product_data in products_data:
            if not all(k in product_data for k in ('id', 'quantityInStock')):
                return Response({"error": "Invalid product data"}, status=HTTP_400_BAD_REQUEST)

            product_id = product_data.get('id')
            quantityInStock = product_data.get('quantityInStock')

            if product_id is None or quantityInStock is None:
                return Response({"error": "Invalid product data"}, status=HTTP_400_BAD_REQUEST)

            try:
                product = InfoProduct.objects.get(tig_id=product_id)
                new_stock = product.quantityInStock + int(quantityInStock)

                if new_stock >= 0:
                    product.quantityInStock = new_stock
                    product.save()
                else:
                    return Response({'error': f'Invalid quantityInStock for product {product_id}'}, status=HTTP_400_BAD_REQUEST)

            except InfoProduct.DoesNotExist:
                return Response({"error": f"Product {product_id} not found"}, status=HTTP_400_BAD_REQUEST)

        return Response({"status": "quantityInStock updated successfully"}, status=HTTP_200_OK)


class UpdateMultipleProductPromotions(APIView):

    def put(self, request, format=None):
        products_data = request.data

        for product_data in products_data:
            if not all(k in product_data for k in ('id', 'sale', 'discount')):
                return Response({"error": "Invalid product data"}, status=HTTP_400_BAD_REQUEST)

            product_id = product_data.get('id')
            sale = product_data.get('sale')
            discount = product_data.get('discount')

            if product_id is None or sale is None or discount is None:
                return Response({"error": "Invalid product data"}, status=HTTP_400_BAD_REQUEST)

            try:
                product = InfoProduct.objects.get(tig_id=product_id)

                # Mise à jour du champ "sale" du produit
                product.sale = sale

                # Mise à jour du champ "discount" du produit
                if 0 <= float(discount) <= 100:
                    product.discount = float(discount)
                    product.price_on_sale = product.price * (1 - float(discount) / 100)
                    product.save()
                else:
                    return Response({'error': f'Invalid discount for product {product_id}'}, status=HTTP_400_BAD_REQUEST)

            except InfoProduct.DoesNotExist:
                return Response({"error": f"Product {product_id} not found"}, status=HTTP_400_BAD_REQUEST)

        return Response({"status": "Promotions updated successfully"}, status=HTTP_200_OK)

# class ChiffreAffaire(APIView):
#     def get(self, request, format=None):
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         category = request.query_params.get('category')

#         # On récupère tous les produits vendus pendant la période spécifiée
#         sold_products = InfoProduct.objects.filter(
#             availableproduct__created__gte=start_date,
#             availableproduct__created__lte=end_date,
#             availableproduct__type='retrait-par-vente'
#         )

#         # On filtre les produits par catégorie si nécessaire
#         if category:
#             sold_products = sold_products.filter(category=category)

#         # On calcule le chiffre d'affaires en additionnant le prix de vente de chaque produit multiplié par la quantité vendue
#         total_sales = 0
#         for product in sold_products:
#             sales_info = product.availableproduct_set.filter(created__gte=start_date, created__lte=end_date, type='retrait-par-vente')
#             total_sales += sum([info.quantity * product.price for info in sales_info])

#         # On retourne le résultat
#         return Response({'chiffre_affaire': total_sales}, status=status.HTTP_200_OK)

class ChiffreAffaire(APIView):
    def get(self, request):
        # Récupérer les paramètres de la requête
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        category = request.query_params.get('category')

        # Préparer les filtres de requête pour la période et la catégorie
        filters = {'created__gte': start_date, 'created__lte': end_date}
        if category:
            filters['product__category'] = category

        # Effectuer la requête pour les ventes correspondantes
        sales = Sale.objects.filter(**filters)

        # Calculer le chiffre d'affaire
        total_sales = 0
        for sale in sales:
            total_sales += sale.price * sale.quantity

        # Retourner le résultat
        return Response({'chiffre_affaire': total_sales}, status=status.HTTP_200_OK)

class ResultatComptable(APIView):
    def get(self, request):
        # Récupérer les paramètres de la requête
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Préparer les filtres de requête pour la période
        filters = {'created__gte': start_date, 'created__lte': end_date}

        # Effectuer la requête pour les lots correspondants
        lots = Lot.objects.filter(**filters)

        # Calculer la marge
        total_invoices = sum(lot.invoice.amount for lot in lots if lot.invoice)
        total_sales = sum(lot.quantity * lot.info_product.price for lot in lots)
        margin = total_sales - total_invoices

        # Calculer le résultat comptable
        annual_margin = margin * 12 / (int(end_date[0:4]) - int(start_date[0:4]) + 1)
        is_tax = max(0, 0.3 * annual_margin)

        # Retourner le résultat
        return Response({
            'resultat_comptable': annual_margin,
            'impot_societes': is_tax
        }, status=status.HTTP_200_OK)



class PromoList(APIView):
    def get(self, request, format=None):
        res = []
        for prod in ProduitEnPromotion.objects.all():
            serializer = ProduitEnPromotionSerializer(prod)
            try:
                product = InfoProduct.objects.get(tig_id=serializer.data['tigID'])
                res.append(product.to_dict())
            except InfoProduct.DoesNotExist:
                pass
        return JsonResponse(res, safe=False)


class PromoDetail(APIView):
    def get_object(self, tig_id):
        try:
            return ProduitEnPromotion.objects.get(tig_id=tig_id)
        except ProduitEnPromotion.DoesNotExist:
            raise Http404

    def get(self, request, tig_id, format=None):
        prod = self.get_object(tig_id)
        serializer = ProduitEnPromotionSerializer(prod)
        try:
            product = InfoProduct.objects.get(tig_id=serializer.data['tigID'])
            return Response(product.to_dict())
        except InfoProduct.DoesNotExist:
            return Response({"error": f"Product {serializer.data['tigID']} not found"}, status=HTTP_400_BAD_REQUEST)


class AvailableList(APIView):
    def get(self, request, format=None):
        res = []
        for prod in AvailableProduct.objects.all():
            serializer = AvailableProductSerializer(prod)
            try:
                product = InfoProduct.objects.get(tig_id=serializer.data['tigID'])
                res.append(product.to_dict())
            except InfoProduct.DoesNotExist:
                pass
        return JsonResponse(res, safe=False)


class AvailableDetail(APIView):
    def get_object(self, pk):
        try:
            return AvailableProduct.objects.get(pk=pk)
        except AvailableProduct.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        prod = self.get_object(pk)
        serializer = AvailableProductSerializer(prod)
        try:
            product = InfoProduct.objects.get(tig_id=serializer.data['tigID'])
            return Response(product.to_dict())
        except InfoProduct.DoesNotExist:
            return Response({"error": f"Product {serializer.data['tigID']} not found"}, status=HTTP_400_BAD_REQUEST)


