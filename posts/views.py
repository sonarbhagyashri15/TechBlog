from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .mongo import blogs_collection
from .models import Blog
from .forms import BlogForm, RegisterForm
import markdown
import re
from django.core.paginator import Paginator
import threading

# CREATE BLOG USERS
@login_required
def create_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            blogs_collection.insert_one({
                "title": blog.title,
                "content": blog.content,
                "tags": blog.tags,
                "author": blog.author,
            })
            thread = threading.Thread(target=background_task)
            thread.start()
            messages.success(request, "Blog Created Successfully!")
            return redirect("blog_list")
    else:
        form = BlogForm()
    return render(request, "create_blog.html", {
        "form": form
    })
    
#CREAT BLOGS ADMIN    
def admin_createblog(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")
    if request.method == "POST":
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            blogs_collection.insert_one({
                "title": blog.title,
                "content": blog.content,
                "tags": blog.tags,
                "author": blog.author,
            })
            thread = threading.Thread(target=background_task)
            thread.start()
            messages.success(request, "Blog Created Successfully!")
            return redirect("manage_blogs")
    else:
        form = BlogForm()
    return render(request, "admin_createblog.html", {
        "form": form
    })

# EDIT BLOG
def edit_blog(request, id):
    if not request.user.is_authenticated and not request.session.get("is_admin"):
        return redirect("login")
    blog = get_object_or_404(Blog, id=id)
    if request.method == "POST":
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            updated_blog = form.save()
            blogs_collection.update_one(
                {"title": blog.title},
                {
                    "$set": {
                        "title": updated_blog.title,
                        "content": updated_blog.content,
                        "tags": updated_blog.tags,
                        "author": updated_blog.author,
                    }
                }
            )
            messages.success(request, "Blog Updated Successfully!")
            if request.session.get("is_admin"):
                return redirect("manage_blogs")
            return redirect("blog_list")
    else:
        form = BlogForm(instance=blog)
    return render(request, "edit_blog.html", {
        "form": form
    })

# VIEW BLOG
@login_required
def view_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    html_content = markdown.markdown(blog.content)
    tags = extract_tags(blog.content)
    emails = extract_emails(blog.content)
    return render(request, "view_blog.html", {
        "blog": blog,
        "html_content": html_content,
        "tags": tags,
        "emails": emails,
    })

# DELETE BLOG
def delete_blog(request, id):
    if not request.user.is_authenticated and not request.session.get("is_admin"):
        return redirect("login")
    blog = get_object_or_404(Blog, id=id)
    if request.method == "POST":
        blogs_collection.delete_one({
            "title": blog.title
        })
        blog.delete()
        messages.success(request,"Blog Deleted Successfully!")
        if request.session.get("is_admin"):
            return redirect("manage_blogs")
        return redirect("blog_list")
    return render(request,"delete_blog.html",{
        "blog":blog
    })

# BLOG LIST
def blog_list(request):
    if not request.user.is_authenticated and not request.session.get("is_admin"):
        return redirect("login")
    search = request.GET.get("search")
    if search:
        blogs=Blog.objects.filter(
            title__icontains=search
        ).order_by("-id")
    else:
        blogs=Blog.objects.all().order_by("-id")
    paginator = Paginator(blogs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog_list.html", {
        "page_obj": page_obj,
        "blogs": page_obj
    })

# SEARCH BLOG
def search_blog(request):
    search = request.GET.get("search")
    if search:
        blogs = Blog.objects.filter(title__icontains=search)
    else:
        blogs = Blog.objects.all()
    return render(request, "blog_list.html", {
        "blogs": blogs
    })

# TAG FILTER
def tag_filter(request, tag):
    blogs = Blog.objects.filter(tags__icontains=tag)
    return render(request, "blog_list.html", {
        "blogs": blogs
    })
    
# REGISTER

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")
        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        messages.success(request, "Registration Successful!")
        return redirect("login")
    return render(request, "register.html")

# LOGIN

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid Username or Password")
    return render(request, "login.html")

# LOGOUT
def logout_user(request):
    logout(request)
    return redirect("login")
# DASHBOARD
def dashboard(request):
    if not request.user.is_authenticated and not request.session.get("is_admin"):
        return redirect("login")
    total_blogs = Blog.objects.count()
    total_users = User.objects.count()
    latest_blogs = Blog.objects.order_by("-id")[:5]
    context = {
        "total_blogs": total_blogs,
        "total_users": total_users,
        "latest_blogs": latest_blogs,
    }
    return render(request, "dashboard.html", context)

def extract_tags(content):
    tags = re.findall(r"#(\w+)", content)
    return tags

def extract_emails(content):
    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        content
    )
    return emails

def background_task():
    print("Search Index Updated Successfully...")
    
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "admin" and password == "admin123":
            request.session["is_admin"] = True
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid Admin Credentials")
    return render(request, "admin_login.html")


def admin_dashboard(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")
    total_blogs = Blog.objects.count()
    total_users = User.objects.count()
    context = {
        "total_blogs": total_blogs,
        "total_users": total_users,
    }
    return render(request, "admin_dashboard.html", context)

from django.contrib.auth.models import User

def manage_users(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")
    users = User.objects.all()
    return render(request, "manage_users.html", {
        "users": users
    })
    
def delete_user(request, id):
    if not request.session.get("is_admin"):
        return redirect("admin_login")
    user = get_object_or_404(User, id=id)
    if request.method == "POST":
        user.delete()
        return redirect("manage_users")
    return render(request, "delete_user.html", {
        "user": user
    })
    
def manage_blogs(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")
    blogs = Blog.objects.all().order_by("-id")
    return render(request, "manage_blogs.html", {
        "blogs": blogs
    })
    
def admin_createblog(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")
    if request.method == "POST":
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            blogs_collection.insert_one({
                "title": blog.title,
                "content": blog.content,
                "tags": blog.tags,
                "author": blog.author,
            })
            messages.success(request, "Blog Created Successfully!")
            return redirect("manage_blogs")
    else:
        form = BlogForm()
    return render(request, "admin_createblog.html", {
        "form": form
    })