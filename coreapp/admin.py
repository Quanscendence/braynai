from django.contrib import admin
from coreapp.models import ProjectType,Project,ProjectUser,FileUpload,ProjectColumn,ProjectJsonStorage,ProjectDashboard, DashboardQuery,ProjectJsonStorageMetadata,ProjectIndex,ProjectBillingPrms, \
                             ProjectBillingHourlyCost, ProjectBillingDayCost, ProjectBillingMonthCost, ProjectPricing,DefaultProjectPricing, ProjectInvoice, Tax,ProjectSchema, ApiDataGet
                             
# Register your models here.




# inside search
# vim: set fileencoding=utf-8 :


from . import models

class ProjectJsonStorageMetadataAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project_json',
        'rows',
        'columns',
    )
    list_filter=('id',)
    search_fields = ('name',)

class PickleUploadAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'pick',
    )
    list_filter = (
        'created',
        'updated',
        'project',
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'pick',
    )
    search_fields = ('name',)


class ProjectJsonStorageAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'js',
        'uploaded',
    )
    list_filter = ('created', 'updated', 'project', 'uploaded')
    search_fields = ('name',)

class IndustryChoicesAdmin(admin.ModelAdmin):

    list_display = (
        'name',
    )
    search_fields = ('name',)




class ProjectTypeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project_id',
        'industry_name',
        'color_code'
    )
    list_filter = ('created', 'updated')
    search_fields = ('name',)


class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'type',
        'admin_user',
    )
    list_filter = (
        'created',
        'updated',
        'admin_user',
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'type',
        'admin_user',
    )
    raw_id_fields = ('type',)
    search_fields = ('name',)


class ProjectUserAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'project_user',
        'contact_no',
        'accept',
    )
    list_filter = (
        'created',
        'updated',
        'project',
        'id',
        'name',
        'description',
        'version',
        'project_user',
        'created',
        'updated',
        'project',
        'contact_no',
        'accept',
    )
    search_fields = ('name',)


class FileUploadAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'file',
    )
    list_filter = (
        'created',
        'updated',
        'project',
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'file',
    )
    search_fields = ('name',)


class ProjectColumnAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'column',
        'start_date',
        'end_date',
    )
    list_filter = (
        'created',
        'updated',
        'project',
        'start_date',
        'end_date',
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'column',
        'start_date',
        'end_date',
    )
    search_fields = ('name',)


class ProjectDashboardAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'updated',
        'project',
        'dashboard_admin_user',
        'report_time',
    )
    list_filter = (
        'updated',
        'project',
        'created',
        'dashboard_admin_user',
        'id',
        'name',
        'description',
        'version',
        'updated',
        'project',
        'dashboard_admin_user',
        'report_time',
    )
    raw_id_fields = ('dashboard_users',)
    search_fields = ('name',)


class PlotAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'plot_type',
        'x_axis',
        'y_axis',
        'z_axis',
        'color',
        
    )
    list_filter = (
        'created',
        'updated',
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'plot_type',
        'x_axis',
        'y_axis',
        'z_axis',
        'color',
    )
    search_fields = ('name',)

class UserNotificationAdmin(admin.ModelAdmin):

    list_display = (


        'user',
        'notification_count',

    )
    list_filter = (

        'user',
        'notification_count',

    )

class ProjectMetaDataAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'updated',
        'project',
        'date_column_name',
        'created',
    )
    list_filter = (
        'updated',
        'project',
        'created',
        'id',
        'name',
        'description',
        'version',
        'updated',
        'project',
        'date_column_name',
        'created',
    )
    search_fields = ('name',)


class ProjectConfigurationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'column_name',
        'user',
        'changed_date',
    )
    list_filter = ('created', 'updated', 'project', 'column_name')
    search_fields = ('name',)

class ProjectQueryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'end_date',
        'start_date',
        'where_query',
        'group_query',
        'aggregation_value',
        'aggregation_query',
        'expected_range',
    )
    list_filter = ('created', 'updated', 'project',)
    search_fields = ('project',)


class DashboardQueryAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'js_storage',
        'end_date',
        'start_date',
        'where_query',
        'group_query',
        'aggregation_value',
        'aggregation_query',
        'expected_range',
    )
    list_filter = ('created', 'updated', 'project',)
    search_fields = ('project',)
class EndPointAlgorithmAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'feature',
        'y_factor',
        'accuracy',
        'type_of_prediction',
        'model_id'

    )
    list_filter = ('created', 'updated', )
    search_fields = ('end_point',)


class ProjectEndPointAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'query',
        'project',
        'sub_df',
        
    )
    list_filter = ('created', 'updated', 'query',)
    search_fields = ('query','project')
class ProjectFileRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'relation'
        
    )
    list_filter = ('created', 'updated', )
    search_fields = ('project',)


class ProjectIndexAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'json_storage',
        'start_date',
        'end_date',
        
    )
    list_filter = ('json_storage',
        'start_date',
        'end_date', )
    search_fields = ('project', 'json_storage',)
class ProjectBillingMonthCostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'project',
        'user_cost',
        'end_point_cost',
        'iqs_cost',
        'disk_space_cost',
        'iqs_count'
        
    )
    list_filter = ('project',
        'user_cost',
        'end_point_cost',
        'iqs_cost',
        'disk_space_cost',
        'iqs_count')
    search_fields = ('project',
        'user_cost',
        'end_point_cost',
        'iqs_cost',
        'disk_space_cost',
        'iqs_count')
admin.site.register(ProjectBillingPrms)
admin.site.register(ProjectBillingHourlyCost)
admin.site.register(ProjectBillingDayCost)
admin.site.register(ProjectPricing)
admin.site.register(DefaultProjectPricing)
admin.site.register(ProjectInvoice)
admin.site.register(Tax)
admin.site.register(ProjectSchema)
admin.site.register(ApiDataGet)



def _register(model, admin_class):
    admin.site.register(model, admin_class)
_register(models.ProjectFileRelationship, ProjectFileRelationshipAdmin)
_register(models.ProjectJsonStorageMetadata, ProjectJsonStorageMetadataAdmin)

_register(models.ProjectIndex, ProjectIndexAdmin)
_register(models.ProjectBillingMonthCost, ProjectBillingMonthCostAdmin)
_register(models.ProjectEndPoint, ProjectEndPointAdmin)
_register(models.EndPointAlgorithm, EndPointAlgorithmAdmin)
_register(models.DashboardQuery, DashboardQueryAdmin)
_register(models.PickleUpload, PickleUploadAdmin)
_register(models.ProjectJsonStorage, ProjectJsonStorageAdmin)
_register(models.ProjectQuery, ProjectQueryAdmin)
_register(models.ProjectType, ProjectTypeAdmin)
_register(models.Project, ProjectAdmin)
_register(models.ProjectUser, ProjectUserAdmin)
_register(models.FileUpload, FileUploadAdmin)
_register(models.ProjectColumn, ProjectColumnAdmin)
_register(models.ProjectDashboard, ProjectDashboardAdmin)
_register(models.Plot, PlotAdmin)
_register(models.UserNotification, UserNotificationAdmin)
_register(models.ProjectMetaData, ProjectMetaDataAdmin)
_register(models.ProjectConfiguration, ProjectConfigurationAdmin)
_register(models.IndustryChoices, IndustryChoicesAdmin)
