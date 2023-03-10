from django.shortcuts import render, redirect, HttpResponse
from library import models
import hashlib
import time
from datetime import datetime, timedelta
from django.db.models import Count
from django.db import connection
from django.core.paginator import Paginator
from faker import Faker
from django.db.models import Q


# Create your views here.
# redirect重定向，跳转到相应的网址
# GET提交的数据会在地址栏中显示出来，而POST提交，地址栏不会改变
# 注册
def pwd_encrypt(password):
    md5 = hashlib.md5()  # 获取md5对象
    md5.update(password.encode())  # 进行更新注意需要使用 字符串的二进制格式
    result = md5.hexdigest()  # 获取加密后的内容
    return result


# 注册
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        password = request.POST.get('password')

        password = pwd_encrypt(password)

        models.Librarian.objects.create(name=username, nick_name=nickname, password=password)

        return redirect('/library/login/')

    return render(request, 'register.html')


def login(request):
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        pwd = pwd_encrypt(pwd)
        ret = models.Librarian.objects.filter(name=username, password=pwd)
        if ret:
            request.session['name'] = username
            library_obj = ret.last()  # 获取library对象
            nickname = library_obj.nick_name
            request.session['nick_name'] = nickname
            password = library_obj.password
            request.session['password'] = password
            request.session['id'] = library_obj.id
            return redirect('/library/index/')
        else:
            error_msg = "用户名或密码错误"

    return render(request, 'login.html', {'error_msg': error_msg})


def logout(request):
    request.session.flush()
    return redirect('/library/login/')


# 装饰器
def library_decorator(func):
    def inner(request, *args, **kwargs):
        username = request.session.get('username')
        nickname = request.session.get('nickname')
        if username and nickname:

            return func(request, *args, **kwargs)
        else:
            return redirect('/library/login/')

    return inner


# @library_decorator
def add_publisher(request):
    if request.method == "POST":
        publisher_name = request.POST.get("name")
        publisher_address = request.POST.get("address")
        models.Publisher.objects.create(name=publisher_name, address=publisher_address)
        return redirect("/library/publisher_list/")
    return render(request, "publisher_add.html")


# @library_decorator
def publisher_list(request, page=1):
    if request.method == "GET":
        publisher_obj_list = models.Publisher.objects.all()
        paginator = Paginator(publisher_obj_list, 10)  # 每页显示10个
        total_page_num = paginator.num_pages  # 总页码
        current_page_num = page if page else request.GET.get("page", 1)
        publisher_page_objs = paginator.page(current_page_num)  # 获取数据进行渲染
        page_range = paginator.page_range
        if total_page_num > 10:
            if current_page_num < 9:  # 当前页小于10时
                page_range = range(1, 11)
            elif current_page_num + 8 > total_page_num:
                page_range = range(current_page_num - 2, total_page_num + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 8)
        else:
            page_range = page_range
        return render(request, "publisher_list.html", locals())


# @library_decorator
def update_publisher(request):
    if request.method == "GET":
        id = request.GET.get("id")
        publisher = models.Publisher.objects.get(id=id)
        return render(request, "publisher_update.html", locals())
    else:
        id = request.POST.get("id")
        names = request.POST.get("name")
        address = request.POST.get("address")
        models.Publisher.objects.filter(id=id).update(name=names, address=address)
        return redirect("/library/publisher_list/")


def delete_publisher(request):
    id = request.GET.get('id')
    publisher = models.Publisher.objects.get(id=id)
    publisher.delete()
    return redirect("/library/publisher_list/")


def book_list(request, page=1):
    if request.method == "GET":
        book_obj_list = models.Books.objects.all()
        paginator = Paginator(book_obj_list, 10)
        total_page_num = paginator.num_pages  # 总页码
        current_page_num = page
        book_page_objs = paginator.page(current_page_num)
        page_range = paginator.page_range
        # 确定页码范围
        if total_page_num > 10:
            if current_page_num < 9:
                page_range = range(1, 11)
            elif current_page_num + 8 > total_page_num:
                page_range = range(current_page_num - 2, total_page_num + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 8)

        return render(request, "book_list.html", locals())


# @library_decorator
def add_book(request):
    if request.method == "GET":
        # 从数据库中查询所有出版社对象
        publisher_list = models.Publisher.objects.all()
        # 将页面转调到添加图书的页面
        return render(request, "book_add.html", locals())
    elif request.method == "POST":
        f = Faker(locale="zh_CN")  # Faker对象
        book_num = f.msisdn()  # 图书编码
        book_name = request.POST.get("book_name")
        author = request.POST.get("author")
        book_type = request.POST.get("book_type")
        book_price = request.POST.get("book_price")
        book_inventory = request.POST.get("book_inventory")
        book_score = request.POST.get("book_score")
        book_description = request.POST.get("book_description")
        book_sales = request.POST.get("book_sales")
        comment_nums = request.POST.get("comment_nums")
        publisher_id = request.POST.get("publisher")
        publisher_obj = models.Publisher.objects.get(id=publisher_id)  # 出版社对象
        book_obj = models.Books.objects.create(
            book_num=book_num,
            book_name=book_name,
            author=author,
            book_type=book_type,
            book_price=book_price,
            book_inventory=book_inventory,
            book_score=book_score,
            book_description=book_description,
            book_sales=book_sales,
            comment_nums=comment_nums,
            publisher=publisher_obj,
        )
        # 使用 FILES.getlist() 来获取 多张图片
        userfiles = request.FILES.getlist('book_image')
        # 循环遍历读取每一张图片保存到images下
        for index, image_obj in enumerate(userfiles):
            name = image_obj.name.rsplit('.', 1)[1]  # 图书格式
            path = 'library/static/images/books/{}_{}.{}'.format(book_name, index, name)  # 图片路径
            # 保存图片
            with open(path, mode='wb') as f:
                for content in image_obj.chunks():
                    f.write(content)

            obj_image = models.Image()
            path1 = 'images/books/{}_{}.{}'.format(book_name, index, name)
            obj_image.img_address = path1
            obj_image.img_label = image_obj.name
            obj_image.books = book_obj
            obj_image.save()
            # 3.重定向到商品列表
        return redirect("/library/book_list")


# @library_decorator
def update_book(request):
    if request.method == "GET":
        id = request.GET.get("id")
        book_obj = models.Books.objects.get(id=id)
        publisher_list = models.Publisher.objects.all()
        return render(request, "book_update.html", locals())

    else:
        id = request.POST.get("id")
        book_name = request.POST.get("book_name")
        book_type = request.POST.get("book_type")
        author = request.POST.get("author")
        book_price = request.POST.get("book_price")
        book_inventory = request.POST.get("book_inventory")
        book_score = request.POST.get("book_score")
        book_description = request.POST.get("book_description")
        book_sales = request.POST.get("book_sales")
        comment_nums = request.POST.get("comment_nums")
        publisher_id = request.POST.get("publisher")
        publisher_obj = models.Publisher.objects.get(id=publisher_id)
        book_obj = models.Books.objects.filter(id=id).update(
            book_name=book_name,
            book_type=book_type,
            author=author,
            book_price=book_price,
            book_inventory=book_inventory,
            book_score=book_score,
            book_description=book_description,
            book_sales=book_sales,
            comment_nums=comment_nums,
            publisher=publisher_obj,
        )
        return redirect("/library/book_list")


def delete_book(request):
    id = request.GET.get('id')
    models.Books.objects.filter(id=id).delete()
    return redirect("/library/book_list")


# @library_decorator
def author_list(request, page=1):
    res_lst = []
    author_obj_list = models.Author.objects.all()
    for author_obj in author_obj_list:
        book_obj_list = author_obj.books.all()
        print(book_obj_list)
        res_dic = {
            "author_obj": author_obj,  # 作者对象
            "book_obj_list": book_obj_list,  # 每个作者的图书列表
        }
        res_lst.append(res_dic)
    paginator = Paginator(res_lst, 10)
    total_page_num = paginator.num_pages
    current_page_num = page
    author_page_objs = paginator.page(current_page_num)
    page_range = paginator.page_range
    # 页码范围
    if total_page_num > 10:
        if current_page_num < 9:
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, "author_list.html", locals())


# @library_decorator
def add_author(request):
    if request.method == "GET":
        book_obj_list = models.Books.objects.all()
        return render(request, 'author_add.html', locals())
    elif request.method == "POST":
        name = request.POST.get('name')
        book_ids = request.POST.getlist('books')
        author_obj = models.Author.objects.create(name=name)
        author_obj.books.set(book_ids)
        return redirect('/library/author_list')


# @library_decorator
def update_author(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        author_obj = models.Author.objects.get(id=id)
        book_obj_list = models.Books.objects.all()
        return render(request, 'author_update.html', locals())
    else:
        id = request.POST.get('id')
        name = request.POST.get('name')
        book_ids = request.POST.getlist('books')
        author_obj = models.Author.objects.filter(id=id).first()
        author_obj.name = name
        author_obj.books.set(book_ids)
        author_obj.save()
        return redirect('/library/author_list')


def delete_author(request):
    id = request.GET.get('id')
    author = models.Author.objects.filter(id=id)
    author.delete()
    return redirect("library:author_list")


def index(request, page=1):
    publisher_num = models.Publisher.objects.count()
    author_num = models.Author.objects.count()
    book_num = models.Books.objects.count()
    user_num = models.User.objects.count()
    # 图书库存
    liter_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="文学")])
    pop_liter_book_inventory = sum(
        [book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="流行")])
    cultural_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="文化")])
    live_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="生活")])
    manage_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="经管")])
    science_book_inventory = sum([book_obj.book_inventory for book_obj in models.Books.objects.filter(book_type="科技")])
    book_type_inventory_list = [liter_book_inventory, pop_liter_book_inventory, cultural_book_inventory,
                                live_book_inventory, manage_book_inventory, science_book_inventory]
    # 销量
    liter_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="文学")])
    pop_liter_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="流行")])
    cultural_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="文化")])
    live_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="生活")])
    manage_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="经管")])
    science_book_sales = sum([book_obj.book_sales for book_obj in models.Books.objects.filter(book_type="科技")])
    book_type_sales_list = [liter_book_sales, pop_liter_book_sales, cultural_book_sales, live_book_sales,
                            manage_book_sales, science_book_sales]
    # 总类的数量
    liter_book_bum = models.Books.objects.filter(book_type="文学").count()
    pop_book_bum = models.Books.objects.filter(book_type="流行").count()
    cultural_book_bum = models.Books.objects.filter(book_type="文化").count()
    live_book_bum = models.Books.objects.filter(book_type="生活").count()
    manage_book_bum = models.Books.objects.filter(book_type="经管").count()
    science_book_bum = models.Books.objects.filter(book_type="科技").count()
    book_type_num_list = [liter_book_bum, pop_book_bum, cultural_book_bum, live_book_bum, manage_book_bum,
                          science_book_bum]
    this_year = time.strftime("%Y", time.localtime(time.time()))
    this_month = "9"
    res = models.User.objects.filter(last_time__month=this_month)
    print(res)
    select = {'day': connection.ops.date_trunc_sql('day', 'last_time')}
    count_data = models.User.objects.filter(last_time__year=this_year, last_time__month=this_month).extra(
        select=select).values('day').annotate(number=Count('id'))
    time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    count_data = models.User.objects.filter(last_time__gte=time_30).extra(select=select).values('day').annotate(
        number=Count('id'))
    day_list = []  # 当月时间列表
    user_num_list = []  # 每天用户登录人数列表
    user_list = []
    for i, obj in enumerate(count_data):
        day_list.append(obj['day'].day)
        user_num_list.append(obj['number'])
    user_login_dict = dict(zip(day_list, user_num_list))
    for day in range(1, 31):
        if day not in day_list:  # 说明这天网站没有用户浏览，用户数据为0
            user_login_dict[day] = 0
    user_login_list = []
    for day in range(1, 31):
        for k, v in user_login_dict.items():
            if day == k:
                user_login_list.append(v)
    book_obj_list = models.Books.objects.filter(book_sales__gt=500).order_by("book_sales")
    paginator = Paginator(book_obj_list, 10)
    total_page_num = paginator.num_pages  # 总页码
    current_page_num = page
    book_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象
    page_range = paginator.page_range
    if total_page_num > 10:
        if current_page_num < 9:
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, 'index.html', locals())


# @library_decorator
def add_user(request):
    if request.method == "GET":
        book_obj_list = models.Books.objects.all()
        return render(request, "user_add.html", locals())

    else:
        name = request.POST.get("name")
        nickname = request.POST.get("nickname")
        phone = request.POST.get("phone")
        books = request.POST.get("books")
        password = request.POST.get("password")
        password = pwd_encrypt(password)
        user_obj = models.User.objects.create(
            name=name,
            nickname=nickname,
            password=password,
            phone=phone,
        )
        user_obj.books.set(books)
        return redirect("/library/user_list")


# @library_decorator
def user_list(request, page=1):
    user_obj_list = models.User.objects.all()
    paginator = Paginator(user_obj_list, 10)
    total_page_num = paginator.num_pages
    current_page_num = page
    user_page_objs = paginator.page(current_page_num)
    page_range = paginator.page_range
    # 当前页
    if total_page_num > 10:
        if current_page_num < 9:
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, "user_list.html", locals())


# @library_decorator
def update_user(request):  # 修改用户
    if request.method == "GET":
        id = request.GET.get("id")
        user_obj = models.User.objects.get(id=id)
        book_obj_list = models.Books.objects.all()
        return render(request, "user_update.html", locals())
    else:
        id = request.POST.get("id")
        phone = request.POST.get("phone")
        nick_name = request.POST.get("nickname")
        password = request.POST.get("password")
        books = request.POST.get("books")

        password = pwd_encrypt(password)

        user_obj = models.User.objects.filter(id=id).first()
        user_obj.password = password
        user_obj.nick_name = nick_name
        user_obj.phone = phone
        user_obj.save()
        user_obj.books.set(books)
        author_obj = models.User.objects.filter(id=id).update(password=password, nickname=nick_name, phone=phone)

        return redirect("/library/user_list")


def delete_user(request):
    id = request.GET.get("id")
    models.User.objects.get(id=id).delete()
    return redirect("library:user_list")


# @library_decorator
def search(request):
    # 要前端中获取用户输入的关键字
    search_keywords = request.POST.get("search_keywords", "")
    # print(search_keywords)    # Q查询模糊查询
    if search_keywords:
        books_obj_list = models.Books.objects.filter(
            Q(book_name__icontains=search_keywords) | Q(
                author__icontains=search_keywords) | Q(book_type__icontains=search_keywords) | Q(book_num=search_keywords))  # icontains是不区分大小写

        publishers_obj_list = models.Publisher.objects.filter(
            Q(name__icontains=search_keywords) | Q(address=search_keywords))

        users_obj_list = models.User.objects.filter(
            Q(name__icontains=search_keywords) | Q(nickname__icontains=search_keywords) | Q(phone=search_keywords))
        if len(books_obj_list) != 0:  # 如果能查询到，前端显示图书查询结果
            books_search_result = True
        elif len(publishers_obj_list) != 0:
            publishers_search_result = True
        elif len(users_obj_list) != 0:
            user_search_result = True
        else:
            error_msg = "没有查询到结果，请重新输入"
    else:
        error_msg = "你输入的信息错误,请重新出入"
    return render(request, "search_result.html", locals())
