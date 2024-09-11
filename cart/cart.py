from biblio_app.models import *
class Cart():
    def __init__(self,request):
        self.session=request.session
        
        #Get the current session key if it exists
        cart=self.session.get('session_key')
        
        #if the user is new no session, create one
        if 'session_key' not in request.session:
            cart = self.session['session_key']={}
        
        #make sure cart is available on all pages of site
        self.cart=cart
        
        
        
        
    
    def add(self,ouvrage):
        ouvrage_isbn = str(ouvrage.ISBN)
        
        if ouvrage_isbn in self.cart:
            print("exemplaire existe")
        else:
             self.cart[ouvrage_isbn] = {
            'ouvrage_isbn': ouvrage.ISBN,
            'titre':ouvrage.titre,
        }
        self.save_to_session()
        
        
    def __len__(self):
        return len(self.cart)
    
    
       

    def save_to_session(self):
        self.session['cart'] = self.cart
        self.session.modified = True
    
    
    def get_exemplaires(self):
        ouvrage_isbn=self.cart.keys()
        ouvrages=Ouvrage.objects.filter(ISBN__in=ouvrage_isbn)
        return ouvrages
    
    def get_quants(self):
        quantites=self.cart
        return quantites
    
    def update(self,product_id,quantity):
        product_id=str(product_id)
        product_qty=int(quantity)
        ##get the cart
        
        ourcart=self.cart
        #uodate dict
        ourcart[product_id]=product_qty
        
        self.session.modified = True
        
        thing=self.cart
        return thing
    
    def delete(self,ouvrage_isbn):
        ouvrage_isbn= str(ouvrage_isbn)
        #delete from dict
        if ouvrage_isbn in self.cart:
            del self.cart[ouvrage_isbn]
            
        self.session.modified=True
    

    
    
    def deleteAll(self):
        cart = self.session['session_key']={}
    

