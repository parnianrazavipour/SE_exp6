

# گزارش پروژه معماری میکروسرویس و استقرار آن با Docker

## مقدمه

در این پروژه ما یک معماری مبتنی بر میکروسرویس ایجاد کرده‌ایم که شامل سه بخش است:

1. **Backend Service**: یک سرویس ساده که عملیات CRUD را بر روی یک پایگاه داده محلی (SQLite) انجام می‌دهد. این سرویس قابلیت توسعه و مقیاس‌پذیری دارد.
2. **Interface Service**: سرویسی که درخواست‌ها را از کاربر دریافت کرده و بدون منطق تجاری خاص، آنها را به Nginx هدایت می‌کند. این سرویس در نقش یک واسطه (مشابه یک لایه فرانت‌اند ساده) عمل می‌کند.
3. **Nginx Service**: یک وب سرور که نقش Load Balancer را بین چندین نمونه (Replica) از سرویس Backend ایفا می‌کند. Nginx درخواست‌ها را بین سرویس‌های Backend که بر روی پورت‌ها و آدرس‌های داخلی شبکه Docker در حال اجرا هستند، توزیع می‌کند.

با استفاده از Docker و Docker Compose، این سه سرویس در قالب کانتینرهای جداگانه اجرا شده و Compose امکان مدیریت، استقرار و مقیاس‌بندی آسان سرویس Backend را فراهم می‌کند.

## معماری سیستم

معماری کلی به این صورت است:

```
[Client] --> [Interface Service (Port:5000)] --> [Nginx (Port:8081)] --> [Backend (3 replicas, Port:5001)]
                                                 | 
                                                 --> [Shared Database - SQLite]
```

- درخواست‌های کاربر از طریق پورت 5000 (Interface) دریافت و به Nginx ارسال می‌شوند.
- Nginx به عنوان یک Load Balancer درخواست‌ها را بین سرویس‌های Backend توزیع می‌کند.
- هر سرویس Backend به یک پایگاه داده SQLite اشتراکی دسترسی دارد.
- از Docker Compose برای ساخت و اجرای همزمان سرویس‌ها و از قابلیت `scale` برای افزایش تعداد نمونه‌های Backend استفاده شده است.


## اجزای پروژه و فایل‌ها

- **backend/**  
  شامل کد سرویس Backend و یک فایل `Dockerfile` برای ساخت ایمیج Docker.

- **interface/**  
  شامل کد سرویس Interface و یک فایل `Dockerfile` برای ساخت ایمیج Docker.

- **nginx.conf**  
  فایل پیکربندی Nginx برای هدایت درخواست‌ها به سرویس‌های Backend.

- **docker-compose.yml**  
  فایل Compose که شبکه، سرویس‌ها، وابستگی‌ها، volumeها و scaling را تعریف می‌کند.



## نحوه ساخت و اجرای سرویس‌ها

### پیش‌نیازها

- نصب Docker و Docker Compose
- اطمینان از دسترسی به اینترنت برای کشیدن ایمیج‌های پایه

### ساخت و اجرا

دستورات زیر را در پوشه اصلی پروژه اجرا کنید:

```bash
docker compose up --build --scale backend=3
```

گزینه `--build` باعث Build شدن ایمیج‌ها از Dockerfile‌ها می‌شود.  
گزینه `--scale backend=3` تعداد سه Replica از سرویس Backend را بالا می‌آورد.



![image](https://github.com/user-attachments/assets/a6470128-3d86-4243-bd8a-9835f97374a5)


![image](https://github.com/user-attachments/assets/2fec3bd5-e361-4bc2-aa5b-d5d31eb1700e)



پس از اجرای موفق، سه سرویس به طور همزمان در حال اجرا خواهند بود:

- سرویس Backend بر روی یک شبکه داخلی Docker با سه نسخه (Replica)
- سرویس Interface بر روی پورت 5000
- سرویس Nginx بر روی پورت 8081 (داخل Docker Network، اما توسط Interface قابل دسترسی است)

### بررسی سرویس‌ها

برای مشاهده کانتینرهای در حال اجرا:

```bash
docker container ls
```


![image](https://github.com/user-attachments/assets/5204f0eb-c774-4957-aab6-5a27f33c7d5b)


برای مشاهده ایمیج‌های ساخته شده:

```bash
docker image ls
```

![image](https://github.com/user-attachments/assets/69e39217-e6b4-476b-94ff-4a2633f9da5c)

## تست عملکرد

با فرض اینکه Docker Compose بالا است، می‌توان درخواست‌هایی را از طریق Interface ارسال کرد:

### تست GET

```bash
curl -X GET http://localhost:5000/api/data
```

این درخواست توسط Interface دریافت، به Nginx و سپس به یکی از سرویس‌های Backend ارسال می‌شود. در خروجی یک آرایه JSON از رکوردهای موجود در پایگاه داده دریافت خواهید کرد.




### تست POST

```bash
curl -X POST -H "Content-Type: application/json" \
    -d '{"name": "example", "value": "42"}' \
    http://localhost:5000/api/data
```
در عکس زیر عملیات اضافه کردن رکورد جدید ( برای مثال کالا به همراه ارزش یا قیمت آن) و لیست کردن آن مشاهده میشود.


![image](https://github.com/user-attachments/assets/9394fa48-f26a-4914-b915-4f02c65d145f)


این درخواست یک رکورد جدید در پایگاه داده ایجاد می‌کند. پاسخ در قالب JSON با پیام `Record added` برمی‌گردد.


با تکرار چندین بار درخواست GET می‌توانید در لاگ‌ها مشاهده کنید که درخواست‌ها بین سه Replica از Backend توزیع می‌شوند. این امر نشان‌دهنده‌ی Load Balancing توسط Nginx است.

![image](https://github.com/user-attachments/assets/637185e3-c40e-4c0e-b37f-3d3c8e580d1f)

خروجی دستور sudo docker compose logs -f backend در ترمینال دیگر:


![image](https://github.com/user-attachments/assets/0df0ad42-53d6-410d-bc8b-65956cb59059)


## Scaling (مقیاس‌پذیری)

با تغییر تعداد Replicaها می‌توان توان پردازشی را افزایش یا کاهش داد. به عنوان مثال، اگر بخواهید تعداد Replica را به 5 برسانید:

```bash
docker compose up --build --scale backend=5
```

بدون تغییر در کد، به سادگی تعداد سرویس‌های Backend را افزایش داده‌اید و Nginx به صورت خودکار بین آنها Load Balance انجام می‌دهد.


![image](https://github.com/user-attachments/assets/63dfc3dd-4319-4613-a8e3-7c7a66f17fd9)




![image](https://github.com/user-attachments/assets/74567f32-998f-4ddd-b224-9bb1f078f2c7)




![image](https://github.com/user-attachments/assets/bfc30ba7-ca66-4e43-b798-dfe3398dd77a)




## نتیجه‌گیری

این پروژه یک پیاده‌سازی ساده از معماری میکروسرویس با استفاده از Docker را نشان داد. ما یک سرویس Backend را با چندین Replica راه‌اندازی کردیم، با یک Reverse Proxy (Nginx) Load Balancing کردیم و یک لایه Interface را نیز بین Client و Nginx قرار دادیم. همچنین توانستیم با تغییر تعداد Replicaهای Backend بدون تغییر در کد یا معماری کلی، مقیاس‌پذیری را به راحتی نشان دهیم.

با اجرای این پروژه با Docker و Compose، به راحتی سرویس‌ها را بالا آورده، تست کرده و قابلیت Scale کردن Backend را مشاهده کردیم.

