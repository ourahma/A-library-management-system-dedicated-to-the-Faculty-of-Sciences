from .cart import Cart


# create context processes

def cart(request):
    #return the defualt data from our cart
    #provide data in the context of all templates
    return {'cart':Cart(request)}