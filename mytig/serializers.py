from rest_framework.serializers import ModelSerializer
from mytig.models import ProduitEnPromotion
from mytig.models import AvailableProduct
from mytig.models import InfoProduct

class ProduitEnPromotionSerializer(ModelSerializer):
    class Meta:
        model = ProduitEnPromotion
        fields = ('id', 'tigID')
        
class AvailableProductSerializer(ModelSerializer):
    class Meta:
        model = AvailableProduct
        fields = ('id', 'tigID')        

class InfoProductSerializer(ModelSerializer):
    class Meta:
        model = InfoProduct
        fields = ('id', 'tig_id', 'name', 'category', 'price', 'unit', 'availability', 'sale', 'discount', 'comments', 'owner', 'quantityInStock')
