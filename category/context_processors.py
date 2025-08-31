from .models import Category

def menu_links(request):
    links =Category.objects.all() #this get all the category from model of category from database
    return dict(link=links) # this will be use in another pages for catagories 

