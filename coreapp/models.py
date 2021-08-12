from django.db import models
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User,Group
from coreapp.choices import type_choices,industry_choices,GENDER_CHOICES,PROJECT_TYPE,dashboard_choices,PLOT_CHOICES, DATA_UPLOAD_RANGE_CHOICES, PROJECT_DURATION_CHOICES, PROJECT_DASHBOARD_PERMISSION_CHOICES,INVOICE_STATUS_CHOICES,PLOT_ORIENTATION_CHOICES,TYPE_OF_PREDICTION_CHOICES,API_REQUEST_CHOICES
###search###
from django.db.models import Q

from picklefield.fields import PickledObjectField
import jsonfield

###notification###
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
# Create your models here.
import collections
from engine import cleaner


################## base #############
class Base(models.Model):
    '''
    A Base case mostly common for all the implementations
    '''
    name        = models.CharField(default="Unknown...", max_length=200,blank=True, null=True)
    description = models.TextField(default="some text...",blank=True, null=True)
    version     = models.PositiveIntegerField(blank=True, null=True)
    created     = models.DateTimeField('Created date', auto_now_add=True,
                                   auto_now=False,
                                   null=True, blank=True)
    updated     = models.DateTimeField('Updated date', auto_now_add=False,auto_now=True,null=True, blank=True)
    class Meta(object):
        abstract=True
        #unique_together = (("name", "version"),)
        ordering=('name',)

    def __str__(self):
        return self.name

#################### core code ##################

class PickleUpload(Base):
    """
    TODO: Code not used
    """
    project       = models.ForeignKey('Project', on_delete=models.CASCADE)
    pick          = PickledObjectField()

# TODO: Decide and pick Pickle or Json; don't implement both!

class ProjectJsonStorage(Base):
    '''This is the base class for converting uploade files to json field and storing it.
    all json fields will be under project scope'''
    project       = models.ForeignKey('Project', on_delete=models.CASCADE)
    js            = jsonfield.JSONField()
    columns       = jsonfield.JSONField(null=True,blank=True)
    uploaded      = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.project)

class ProjectIndex(Base):
    '''This is the base class for Storing Meta data of uploads.
    all Row indexes  will be under project scope'''
    project       = models.ForeignKey('Project', on_delete=models.CASCADE)
    json_storage  = models.ForeignKey('ProjectJsonStorage', on_delete=models.CASCADE)
    start_date    = models.DateTimeField(auto_now_add=False)
    end_date      = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return str(self.project)


class Plot(Base):
    '''Model to save the Specific graph Configuration under each dashboard'''
    plot_type   = models.CharField(max_length=20, choices=PLOT_CHOICES)
    x_axis      = models.CharField(max_length=200,null=True,blank=True)
    y_axis      = models.CharField(max_length=200,null=True,blank=True)
    z_axis      = models.CharField(max_length=200,null=True,blank=True)
    color       = models.CharField(max_length=200,null=True,blank=True)
    legend      = models.BooleanField(default=False)
    values      = models.CharField(max_length=200,null=True,blank=True)
    names       = models.CharField(max_length=200,null=True,blank=True)
    size        = models.CharField(max_length=200,null=True,blank=True)
    hover_name  = models.CharField(max_length=200,null=True,blank=True)
    facet_col   = models.CharField(max_length=200,null=True,blank=True)
    orientation = models.CharField(max_length=10,choices=PLOT_ORIENTATION_CHOICES,null=True,blank=True)
    # dashboard_query=models.ForeignKey(DashboardQuery,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return str(self.plot_type)

class ProjectQuery(Base):
    '''this  model is to store user project queries'''
    query_id = models.CharField(max_length=200,blank=True, null=True)
    project       = models.ForeignKey('Project', on_delete=models.CASCADE)
    # js_storage    = jsonfield.JSONField(blank=True, null=True)
    # js_storage  is not been used because

    start_date        = models.CharField(max_length=200,blank=True, null=True)
    end_date          = models.CharField(max_length=200,blank=True, null=True)
    start_date_select = models.CharField(max_length=200,blank=True, null=True)
    end_date_select   = models.CharField(max_length=200,blank=True, null=True)
    where_query       = models.CharField(max_length=2000,blank=True, null=True)
    group_query       = models.CharField(max_length=1000,blank=True, null=True)
    aggregation_value = models.CharField(max_length=200,blank=True, null=True)
    aggregation_query = models.CharField(max_length=2000,blank=True, null=True)
    expected_range    = models.CharField(max_length=200,blank=True, null=True)
    plot              = models.ForeignKey(Plot, on_delete=models.CASCADE,null=True,blank=True)

#
# class Notification(models.Model):
#     recipient = models.ForeignKey(User,
#                                   related_name='notifications_receiver',
#                                   on_delete=models.CASCADE,
#                                   verbose_name=_('Notification receiver'),default='',null=True)
#
#     actor_text = models.ForeignKey(
#         User, related_name='notifications_sender',on_delete=models.CASCADE,blank=True, null=True,
#         verbose_name=_('Anonymous text for actor'))
#
#
#     verb = models.CharField(max_length=100,
#                             verbose_name=_('Verb of the action'))






class ProjectManager(models.Manager):
    '''Model to implement Search project'''
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(title__icontains=query) |
                         Q(date__icontains=query)|
                         Q(type__type__icontains=query)
                        )


'''class to save the different industry names'''
class IndustryChoices(Base):
    pass
    def __str__(self):
        return self.name


class ProjectType(Base):
    '''Model used to create kind of project. ex:Visualization, Interpretation... '''

    project_id=models.CharField(max_length=50)
    industry_name = models.ForeignKey(IndustryChoices,on_delete=models.CASCADE,null=True)
    color_code = models.CharField(max_length=20)

    def __str__(self):
        return self.project_id






class Project(Base):
    '''Base Model to  Create Project '''
    type             = models.ForeignKey(ProjectType,on_delete=models.CASCADE,null=True)
    admin_user       = models.ForeignKey(User, on_delete=models.CASCADE)
    delete_datetime  = models.DateTimeField(null=True,blank=True)
    end_goal         = models.TextField(max_length=2000,null=True,blank=True)
    project_duration = models.CharField(max_length=20,choices=PROJECT_DURATION_CHOICES,null=True,blank=True)
    image            = models.ImageField(null=True,blank=True)
    delete_obj       = models.BooleanField(default=True)
    objects          = ProjectManager()

    def __str__(self):
        return self.name

class ProjectUser(Base):
    '''Model to create projectusers'''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    owner = models.BooleanField(default=False)
    project_user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    contact_no = models.CharField(max_length=14)
    accept=models.CharField(max_length=50,default='False')
    created_time = models.DateTimeField(auto_now_add=True)
    accepted_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.project_user.email)



class FileUpload(Base):
    '''Model to upload additional files by the customer'''
    """
    # TODO: not used
    """
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    file = models.FileField(upload_to ='project_data')

    # def __str__(self):
    #     return str(self.project)

class ProjectColumn(Base):
    '''Model to save the instances of the uploaded file columns'''
    """
    # TODO: not used
    """
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    column=models.CharField(max_length=500)
    column_type =models.CharField(max_length=500)
    start_date=models.DateTimeField(auto_now_add=True)
    end_date=models.DateTimeField(null=True)





'''class to save project metadata details'''
class ProjectMetaData(Base):
    '''Model to save the project meta details'''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    date_column_name = models.CharField(max_length=100,null=True)
    columns = jsonfield.JSONField(null=True,blank=True)
    meta_data          = jsonfield.JSONField(null=True,blank=True)

    def __str__(self):
        return self.project.name

'''class to save the notification to the user'''
class UserNotification(models.Model):
    '''Model to save the notification count'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_count = models.IntegerField(default=0)
    notification_read = models.CharField(max_length=20, default='False')
    def __str__(self):
        return self.user.username

'''class to save the changes in the configuration of the project data'''
class ProjectConfiguration(Base):
    '''Model to save the project meta details'''
    """
    # TODO: not used
    """
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    column_name = models.CharField(max_length=100,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    changed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.column_name



class EndPointAlgorithm(Base):
    '''model to attach query to inference model'''
    feature            = models.CharField(max_length=1000)
    accuracy           = models.CharField(max_length=100,null=True)
    type_of_prediction = models.CharField(choices=TYPE_OF_PREDICTION_CHOICES,max_length=100)
    y_factor           = models.CharField(max_length=100,blank=True,null=True)
    model_id           = models.CharField(max_length=1000)
    model_size         = models.FloatField(default=0.0)
    no_of_group        = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.model_id


class ProjectEndPoint(Base):
    '''model to create an end point
        which will include an query,plot, inference algorithm '''
    query            = models.ForeignKey(ProjectQuery,on_delete=models.CASCADE)
    project          = models.ForeignKey('Project', on_delete=models.CASCADE)
    plot             = models.ForeignKey(Plot,on_delete=models.CASCADE,null=True,blank=True)
    algorithm        = models.ForeignKey(EndPointAlgorithm,on_delete=models.CASCADE,null=True,blank=True)
    sub_df           = jsonfield.JSONField(null=True,blank=True)
    sub_df_frequency = models.CharField(max_length=30,choices=DATA_UPLOAD_RANGE_CHOICES,null=True)
    user             = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    alignment_object = jsonfield.JSONField(blank=True, null=True)
    def __str__(self):
        return self.name


class ProjectDashboard(Base):
    '''Model to implement dashboard,
    dashboard will be  the report for users to see there data results'''
    project              = models.ForeignKey(Project,on_delete=models.CASCADE)
    additional_email     = models.CharField(max_length=500,null=True,blank=True)
    report_frequency     =  models.CharField(max_length=500,choices=DATA_UPLOAD_RANGE_CHOICES,null=True,blank=True)
    dashboard_admin_user =models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    dashboard_users      =models.ManyToManyField(User, related_name="dashboard_users",null=True,blank=True)
    end_point            = models.ManyToManyField(ProjectEndPoint, related_name="dashboard_users")
    comment              = models.TextField(null=True,blank=True)
    report_time          = models.DateTimeField(auto_now_add=True)
    algorithm            = models.CharField(max_length=500,null=True,blank=True)
    dashboard_for        = models.CharField(max_length=30,choices=PROJECT_DASHBOARD_PERMISSION_CHOICES)
    hash_code             = models.CharField(max_length=100,null=True,blank=True)
    dashboard_format     = jsonfield.JSONField(blank=True, null=True)
    public_shared_code    = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.name

class DashboardQuery(Base):
    '''this  model is to store user project queries'''
    """
    # TODO: not used
    """
    query_id = models.CharField(max_length=200,blank=True, null=True)
    dashboard = models.ForeignKey(ProjectDashboard,on_delete=models.CASCADE, null=True)
    project       = models.ForeignKey('Project', on_delete=models.CASCADE)
    js_storage    = jsonfield.JSONField(blank=True, null=True)
    start_date    = models.CharField(max_length=200,blank=True, null=True)
    end_date    = models.CharField(max_length=200,blank=True, null=True)
    where_query    = models.CharField(max_length=200,blank=True, null=True)
    group_query    = models.CharField(max_length=200,blank=True, null=True)
    aggregation_value = models.CharField(max_length=200,blank=True, null=True)
    aggregation_query  = models.CharField(max_length=200,blank=True, null=True)
    expected_range     = models.CharField(max_length=200,blank=True, null=True)

    def __str__(self):
        return self.query_id







class ProjectFileRelationship(Base):
    ''' table to build the relationship btw files '''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    relation    = jsonfield.JSONField()
    relation_mapping    = jsonfield.JSONField()
    def __str__(self):
        return str(self.project)



class ProjectTemp(Base):
    '''temporary model to keep tarck of data upload in project creation process'''
    '''
    # TODO: not used
    '''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    file_1 = models.FileField(null=True,blank=True)
    file_2 = models.FileField(null=True,blank=True)
    file_3 = models.FileField(null=True,blank=True)
    file_1_header = models.BooleanField(default=True)
    file_2_header = models.BooleanField(default=True)
    file_3_header = models.BooleanField(default=True)
    file_1_delimiter = models.CharField(max_length=2,null=True,blank=True)
    file_2_delimiter = models.CharField(max_length=2,null=True,blank=True)
    file_3_delimiter = models.CharField(max_length=2,null=True,blank=True)



class ProjectSchema(Base):
    ''' table to build the relationship btw files '''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    schema    = jsonfield.JSONField()
    def __str__(self):
        return str(self.project)


class ProjectFilename(Base):
    '''to store the project files names'''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    file_name = models.CharField(max_length=200,null=True)
    file = models.FileField(null=True)
    def __str__(self):
        return self.file_name


class DataFrameDisplay(Base):
    '''to store the and display the row filtered data from the project dataframe'''
    project   = models.ForeignKey(Project,on_delete=models.CASCADE)
    from_row = models.PositiveIntegerField()
    to_row   = models.PositiveIntegerField()
    df       = jsonfield.JSONField()
    user      = models.ForeignKey(User,on_delete=models.CASCADE)

    def  __str__(self):
        return str(self.project)+str(self.user)




class ProjectJsonStorageMetadata(Base):
    ''' to store the projectjson no of rows ,  columns,'''
    project_json  = models.OneToOneField(ProjectJsonStorage,on_delete=models.CASCADE)
    rows          = models.PositiveIntegerField()
    columns       = models.PositiveIntegerField()
    head_json     = jsonfield.JSONField()
    tail_json     = jsonfield.JSONField()

    def __str__(self):
        return str(self.project_json)+"_"+str(self.rows)+":"+str(self.columns)


class ProjectBillingPrms(Base):
    '''class to keep track of query opened time in an project'''
    query_count = models.PositiveIntegerField(default=0)
    user        = models.PositiveIntegerField(default=0)
    end_point   = models.PositiveIntegerField(default=0)
    project     = models.OneToOneField(Project,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.query_count)+str(self.project)

class ProjectBillingHourlyCost(Base):
    '''class to track the hourly billing of project'''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    disk_space_cost = models.FloatField(default=0.0)
    user_cost = models.FloatField(default=0.0)
    end_point_cost = models.FloatField(default=0.0)
    def __str__(self):
        return str(self.project)


class ProjectBillingDayCost(Base):
    '''class to track the hourly billing of project'''
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    disk_space_cost = models.FloatField(default=0.0)
    user_cost = models.FloatField(default=0.0)
    end_point_cost = models.FloatField(default=0.0)
    iqs_cost       = models.FloatField(default=0.0)
    def __str__(self):
        return str(self.project)


class ProjectBillingMonthCost(Base):
    '''class to track the hourly billing of project'''
    project         = models.ForeignKey(Project,on_delete=models.CASCADE)
    disk_space_cost = models.FloatField(default=0.0)
    user_cost       = models.FloatField(default=0.0)
    end_point_cost  = models.FloatField(default=0.0)
    custom_supprt   = models.FloatField(default=0.0)
    monthly_maintenance= models.FloatField(default=49)
    iqs_cost        = models.FloatField(default=0.0)
    iqs_count       = models.PositiveIntegerField(default=0)
    disk_space_count =  models.PositiveIntegerField(default=0)
    def __str__(self):
        return str(self.project)

class DefaultProjectPricing(Base):
    '''class to manage the pricing of the billing in project'''

    user                 = models.FloatField(default=0.0)
    end_point            = models.FloatField(default=0.0)
    iqs                  = models.FloatField(default=0.0)
    disk_space           = models.FloatField(default=0.0)
    free_tire            = models.BooleanField(default=False)
    monthly_maintenance  = models.FloatField(default=49)
    custom_supprt   = models.FloatField(default=0.0)
    def __str__(self):
        return self.name

class ProjectPricing(Base):
    '''class to manage the pricing of the billing in project'''
    project    = models.ForeignKey(Project,on_delete= models.CASCADE,null=True,blank=True)
    user       = models.FloatField(default=0.0)
    end_point  = models.FloatField(default=0.0)
    iqs        = models.FloatField(default=0.0)
    disk_space = models.FloatField(default=0.0)
    free_tire  = models.BooleanField(default=False)
    custom_supprt = models.FloatField(default=0.0)
    monthly_maintenance = models.FloatField(default=49)

    def __str__(self):
        return str(self.project)

class ProjectInvoice(Base):
    ''' class to create an monthly invoice monthly'''
    invoice_id      = models.CharField(max_length=20)
    from_date       = models.DateTimeField(auto_now_add=False)
    to_date         = models.DateTimeField(auto_now_add=False)
    bill_amount     = models.FloatField(default=0.0)
    tax_amount      = models.FloatField(default=0.0)
    total_amount    = models.FloatField(default=0.0)
    discount_amount = models.FloatField(default=0.0)
    transaction_id  = models.CharField(max_length=20,null=True,blank=True)
    status          = models.CharField(max_length=30,choices=INVOICE_STATUS_CHOICES,default="Unpaid")
    monthly_cost    = models.ForeignKey(ProjectBillingMonthCost, on_delete=models.CASCADE)
    def __str__(self):
        return self.invoice_id

class Tax(Base):
    tax_percentage     = models.PositiveIntegerField()
    tax_representation = models.CharField(max_length=30,null=True,blank=True)
    tax_no             = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class ApiDataGet(Base):
    project   = models.ForeignKey(Project,on_delete=models.CASCADE )
    api       = models.CharField(max_length=1000)
    basic_key = models.CharField(max_length=1000,null=True,blank=True)
    frequency = models.CharField(max_length=30,choices=DATA_UPLOAD_RANGE_CHOICES)

    def __str__(self):
        return str(self.project)


class EndpointMlApi(Base):
    user      = models.ForeignKey(User,on_delete=models.CASCADE)
    end_point = models.ForeignKey(ProjectEndPoint,on_delete=models.CASCADE)
    api       = models.CharField(max_length=500,null=True,blank=True)
    token     = models.CharField(max_length=100,null=True,blank=True)
    status    = models.CharField(max_length=20,choices=API_REQUEST_CHOICES,default="OPEN")

    def __str__(self):
        return str(self.user)+'_'+str(self.end_point.name)


class EndPointNewColumn(Base):
    ''' class to add new columns to the sub_df'''
    end_point   = models.ForeignKey(ProjectEndPoint,on_delete=models.CASCADE)
    column_name = models.CharField(max_length=500)
    formula     = models.TextField()

    def __str__(self):
        return str(self.end_point)+'_'+self.column_name



