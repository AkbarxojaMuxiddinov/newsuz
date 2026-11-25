from django.core.exceptions import ValidationError

def validate_news_image_size(image):
    if image.size > 5 * 1024 * 1024:
        raise ValidationError(
            "Ynagilik rasimi hajmi 5 mb dan oshmasligi kerak"
        )