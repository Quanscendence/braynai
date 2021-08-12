from django.db import models

from django.utils.text import slugify

# Create your models here.
class Blog(models.Model):
    '''creating different fields for a blog'''
    main_title          = models.CharField(max_length=100)
    single_line_body    = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    date_of_publish     = models.DateField()
    image               = models.ImageField(upload_to='blog_image')
    seo_title           = models.CharField(max_length=50,null=True)
    seo_description     = models.TextField(null=True)
    seo_keyword         = models.CharField(max_length=50,null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.main_title)
        super(Blog, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return '/blog/' + self.slug



class BlogComment(models.Model):
    '''creating different fields for comments by the user'''
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    email_id   = models.EmailField()
    comment    = models.TextField()
