from django.db import models


# Create your model
class ProductPrice(models.Model):
    source = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    price = models.FloatField()
    url = models.URLField()
    image_url = models.URLField()

    def __str__(self):
        return f"{self.product_name} - {self.source} - ${self.price}"


class ProductPriceHistory(models.Model):
    product = models.ForeignKey(ProductPrice, on_delete=models.CASCADE)
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
