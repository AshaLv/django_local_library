from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from .forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

# Create your views here.

def index(request):
	#View function for home page of site

	#Generate counts of some of the main objects
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	#Available books (status = 'a')
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()
	num_authors = Author.objects.count() #the 'all()' is implied by default

	#existing number of genre
	num_genres = Genre.objects.count()

	#existing number of paticular book
	num_paticular_books = Book.objects.filter(title__icontains='加尔文').count()

	#NUmber of visits to this view, as counted in the session variable.
	num_visits = request.session.get('num_visits',0)
	request.session['num_visits'] = num_visits + 1

	#Render the HTML template index.html with the data in the context variables
	return render(
		request,
		'index.html',
		context={'num_books':num_books, 'num_instances':num_instances, 'num_instances_available':num_instances_available, 
		'num_authors':num_authors, 'num_genres':num_genres, 'num_paticular_books':num_paticular_books, 'num_visits':num_visits},
	)

#class based view book list view
class BookListView(generic.ListView):
	model = Book
	paginate_by = 10
	#context_object_name = 'book_list' #your own name for the list as a template variable
	#queryset = Book.objects.all()[:3]
	#template_name = 'books/book_list.html' #specify your own template name/location

#class based view book detail view
class BookDetailView(generic.DetailView):
	model = Book
	def book_detail_view(request,pk):
		try:
			book_id = Book.objects.get(pk=pk)
		except Book.DoesNotExist:
			raise Http404("Book dose not exist")


		#book_id = get_object_or_404(Book, pk=pk)

		return render(
			request,
			'catalog/book_detail.html',
			context={'book':book_id,}
		)

#Author class based list view
class AuthorListView(generic.ListView):
	model = Author
	paginate_by = 10
	#template_location = 'authors/author_list.html' #specify your own template name/location

#class based view author detail view
class AuthorDetailView(generic.DetailView):
	model = Author
	def author_detail_view(request,pk):
		try:
			author_id = Author.objects.get(pk=pk)
		except Author.DoesNotExist:
			raise Http404("Author dose not exist")


		#book_id = get_object_or_404(Book, pk=pk)

		return render(
			request,
			'catalog/author_detail.html',
			context={'author':author_id,}
		)

#class based view for  specific on loaned books
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	#Generic class based view listing books on loan to current user.
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

#class based view for all on loaned books
class AllBorrowedBooksByUserListView(PermissionRequiredMixin, generic.ListView):
	permission_required = 'catalog.can_mark_returned'
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_all.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@permission_required('catalog.can_mark_returned')
def  renew_book_librarian(request, pk):
	book_inst = get_object_or_404(BookInstance, pk = pk)

	#If this is a POST request then process the Form data
	if request.method == 'POST':

		#Create a form instance and populate it with data from the request(binding)
		form = RenewBookForm(request.POST)

		#Check if the form is valid:
		if form.is_valid():
			# Process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_inst.due_back = form.cleaned_data['renewal_date']
			book_inst.save()

			#redirect to a new URL:
			return HttpResponseRedirect(reverse('all-borrowed'))
	#if this is a GET (or any other method) create the default form.
	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

	return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

class AuthorCreate(PermissionRequiredMixin,CreateView):
	permission_required = 'catalog.can_mark_returned'
	model = Author
	fields = '__all__'
	initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
	permission_required = 'catalog.can_mark_returned'
	model = Author
	fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(PermissionRequiredMixin,DeleteView):
	permission_required = 'catalog.can_mark_returned'
	model = Author
	success_url = reverse_lazy('authors')

class BookCreate(PermissionRequiredMixin,CreateView):
	permission_required = 'catalog.can_mark_returned'
	model = Book
	fields = '__all__'

class BookUpdate(PermissionRequiredMixin,UpdateView):
	permission_required = 'catalog.can_mark_returned'
	model = Book
	fields = ['summary','genre']

class BookDelete(PermissionRequiredMixin,DeleteView):
	permission_required = 'catalog.can_mark_returned'
	model = Book
	success_url = reverse_lazy('books')
