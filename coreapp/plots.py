import pandas as pd
import plotly.offline as opy
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from coreapp.models import Plot,ProjectEndPoint,ProjectQuery

class PlotRender:
    def __init__(self,df):
        self.df = df

    def line_plot(self,x,y,color=None,legend=None):
        ''' function for line plot'''
        df = self.df
        if color:

            fig = px.line(df, x=x, y=y, color=color)
        else:
            fig = px.line(df, x=x, y=y)
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div

    def scatter_plot(self,x,y,color=None,legend=None):
        ''' function for scatter plot'''
        # #print("scatter plot with color")
        df=self.df
        if color:
            # #print("scatter plot with color")
            # fig = px.pie(df, values=y, names=x, title='Population of European continent')
            # fig = px.imshow(df )
            fig= px.scatter(df, x=x, y=y, color=color)
            # fig = px.box(df ,x=x, y=y)
            # fig = px.scatter(df ,x=x, y=y,log_y=True, color=color,size="B_current_win_streak",hover_name="location" )
        else:
            # #print("nocolor")
            fig = px.scatter(df ,x=x, y=y)
            # #print("nocolor")
        if legend:
            fig.update_layout(showlegend=False)
        # #print("scatter plot")
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("scatter plot")
        return div


    def box_plot(self,x,y,color=None,legend=None):
        ''' function for box plot'''
        df = self.df
        if color:

            fig = px.box(df, x=x, y=y, color=color)
        else:
            fig = px.box(df, x=x, y=y)
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div

    def bar_plot(self,x,y,color=None,legend=None,orientation='v'):
        ''' function for bar plot'''
        df = self.df
        if color:


            fig =px.bar(df, x=x, y=y, color=color,orientation=orientation)

        else:
            fig = px.bar(df, x=x, y=y,orientation=orientation)

        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div

    def cat_plot(self,x,y,facet_col,color=None,legend=None):
        ''' function for bar plot'''
        #print("cat plot description")
        df = self.df
        if color:

            fig =px.bar(df, x=x, y=y, color=color, barmode="group",
              facet_col=facet_col)
            
        else:
            fig = px.bar(df, x=x, y=y,barmode="group",
              facet_col=facet_col)

        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div

    def histogram_plot(self,x,y,color=None,legend=None):
        ''' function for histogram plot'''
        df = self.df
        # df[x] = df[x].astype('category')
        # a = df[x].cat.codes
        # counts = np.histogram(a)

        if color:
            # fig = px.bar(x=df[x], y=a, labels={'x':x, 'y':'count'})
            fig = px.histogram(df, x=x, y=y,color=color)
        else:
            fig = px.histogram(df, x=x, y=y)
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("called")
        return div

    def count_plot(self,x,color=None,legend=None):
        '''function for count plot'''
        df = self.df
        if color:
            #print("color at plot",color)
            fig = px.histogram(df, x=x, color=color)
        else:
            fig = px.histogram(df, x=x)
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("called")
        return div




    def line_plot_3d(self,x,y,z,color=None,legend=None):
        ''' function for 3d-line plot'''
        df = self.df
        if color:

            fig = px.line_3d(df, x=x, y=y, z=z, color=color)
        else:
            fig = px.line_3d(df, x=x, y=y, z=z)
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div

    def scatter_plot_3d(self,x,y,z,color=None,legend=None):
        ''' function for 3d-scatter plot'''
        df = self.df
        # #print("scatter plot")
        if color:

            fig = px.scatter_3d(df ,x=x, y=y, z=z, color=color )
        else:
            fig = px.scatter_3d(df ,x=x, y=y, z=z )
        # #print("scatter plot")
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("scatter plot")
        return div
    def bubble_plot(self,x,y,size,hover_name,color=None,legend=None):
        df = self.df
        #print("the size",size)
        try:
            df[size] = df[size].astype(float)
        except:
            div=None
            return div
        if color:

            fig= px.scatter(df, x=x, y=y, size=size,hover_name=hover_name,color=color)
        else:
            fig= px.scatter(df, x=x, y=y, size=size,hover_name=hover_name)
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("scatter plot")
        return div

    def pie_plot(self,values,names,legend=None):
        df = self.df
        #print("the values  of pie plot are",values,names)
        try:
            df[values] = df[values].astype(float)
        except:
            div=None
            return div

        fig = px.pie(df, values=values, names=names, title='Pie Chart')
        if legend:
            fig.update_layout(showlegend=False)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("scatter plot")
        return div

    def time_series_plot(self,x,y):
        #print("the x,y",x,y)
        df = self.df
        fig = px.line(df, x=x, y=y)
        div = opy.plot(fig, auto_open=False, output_type='div')
        # #print("scatter plot")
        return div

    def dencity_heatmap_plot(self,x,y):
        df = self.df
        fig = px.density_heatmap(df, x=x, y=y)
        div = opy.plot(fig, auto_open=False, output_type='div')
        return div

class EndPointPlot:
    def __init__(self,df,pk):
        self.df = df
        self.pk = pk


    def update_plot(self,plot_pk,plot_type,x=None,y=None,z=None,color=None,legend=False,size=None,hover_name=None,values=None,names=None,facet_col=None,orientation='h'):
        #print("the facet_col",facet_col)
        update = Plot.objects.filter(pk=plot_pk.pk).update(plot_type=plot_type,x_axis=x,y_axis=y,z_axis=z,color=color,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
        plot = Plot.objects.get(pk=plot_pk.pk)
        df = self.df
        plot_obj = PlotRender(df)
        if plot_type == 'scatter_2d':
            if x and y and color :
                #print("update the plot ",update)
                div = plot_obj.scatter_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.scatter_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'scatter_3d':
            if x and y and z and color:
                div = plot_obj.scatter_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.scatter_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_3d':
            if x and y and z and color :
                div = plot_obj.line_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.line_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_2d':
            if x and y and color :
                div = plot_obj.line_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.line_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend)
                error =False
            else:
                error =True

        elif plot_type == 'horizontal_bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,orientation='h')
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend,orientation='h')
                error =False
            else:
                error =True

        elif plot_type == 'histogram':
            if x and y and color :
                div = plot_obj.histogram_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.histogram_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'box_plot':
            if x and y and color :
                div = plot_obj.box_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.box_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'bubble_plot':
            #print("the bubble plot",x,y,color)
            if x and y and color :
                #print("with color")
                div = plot_obj.bubble_plot(x,y,size,hover_name,color=color,legend=legend)
                #print("the div is",div)
                error =False
            elif x and y:
                #print("without colou")
                div = plot_obj.bubble_plot(x,y,size,hover_name)
                #print("the div is",div)
                error =False
            else:

                error =True
            #print("the div is",div)
            
        elif plot_type == 'pie_chart':
                #print("called pie chart",values,names)
                div = plot_obj.pie_plot(values=values,names=names,legend=legend)
                error =False
        elif plot_type == 'time_series_plot':

            if x and y:
                    div = plot_obj.time_series_plot(x,y)
                    error =False
            else:

                error =True
        elif plot_type == 'heatmap':

                if x and y:
                    div = plot_obj.dencity_heatmap_plot(x,y)
                    error =False
                else:

                    error =True
        elif plot_type == 'count':
            if x and color :
                div = plot_obj.count_plot(x,color=color)
                error =False
            if x :
                div = plot_obj.count_plot(x)
                error =False
            else:
                error =True
        elif plot_type == 'cat':
            if x and y and color and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col,color=color)
            elif x and y and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col)
        #print("the div is",div)
        return div


    def create_plot(self,plot_type,x=None,y=None,z=None,color=None,legend=False,size=None,hover_name=None,values=None,names=None,facet_col=None,orientation='h'):
        plot = Plot.objects.create(plot_type=plot_type,x_axis=x,y_axis=y,z_axis=z,size=size,color=color,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)

        df = self.df
        pk = self.pk
        update = ProjectEndPoint.objects.filter(pk=pk).update(plot=plot)
        plot_obj = PlotRender(df)
        if plot_type == 'scatter_2d':
            if x and y and color :
                div = plot_obj.scatter_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.scatter_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'scatter_3d':
            if x and y and z and color:
                div = plot_obj.scatter_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.scatter_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_3d':
            if x and y and z and color :
                div = plot_obj.line_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.line_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_2d':
            if x and y and color :
                div = plot_obj.line_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.line_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend)
                error =False
            else:
                error =True

        elif plot_type == 'horizontal_bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,orientation='h')
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend,orientation='h')
                error =False
            else:
                error =True


        elif plot_type == 'histogram':
            if x and y and color :
                div = plot_obj.histogram_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.histogram_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'box_plot':
            if x and y and color :
                div = plot_obj.box_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.box_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'bubble_plot':
            if x and y and color :
                div = plot_obj.bubble_plot(x,y,size,hover_name,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.bubble_plot(x,y,size,hover_name)
                error =False
            else:

                error =True
        elif plot_type == 'pie_chart':
                div = plot_obj.pie_plot(values=values,names=names,legend=legend)
                error =False
        elif plot_type == 'time_series_plot':

            if x and y:
                    div = plot_obj.time_series_plot(x,y)
                    error =False
            else:

                error =True
        elif plot_type == 'heatmap':

                if x and y:
                    div = plot_obj.dencity_heatmap_plot(x,y)
                    error =False
                else:

                    error =True
        elif plot_type == 'count':
            if x and color :
                div = plot_obj.count_plot(x,color=color)
                error =False
            if x :
                div = plot_obj.count_plot(x)
                error =False
            else:
                error =True
        elif plot_type == 'cat':
            if x and y and color and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col,color=color)
            elif x and y and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col)

        return div

    def plot(self,plot):
        df = self.df
        x=plot.x_axis
        y=plot.y_axis
        z=plot.z_axis
        color=plot.color
        legend= plot.legend
        values= plot.values
        names=plot.names
        orientation = plot.orientation
        size=plot.size
        hover_name = plot.hover_name
        plot_type =plot.plot_type
        plot_obj = PlotRender(df)
        facet_col = plot.facet_col
        #print("the plot facet",plot.facet_col,plot.id)
        if plot_type == 'scatter_2d':
            if x and y and color :
                div = plot_obj.scatter_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.scatter_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'scatter_3d':
            if x and y and z and color:
                div = plot_obj.scatter_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.scatter_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_3d':
            if x and y and z and color :
                div = plot_obj.line_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.line_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_2d':
            if x and y and color :
                div = plot_obj.line_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.line_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend)
                error =False
            else:
                error =True

        elif plot_type == 'horizontal_bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,orientation='h')
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend,orientation='h')
                error =False
            else:
                error =True

        elif plot_type == 'histogram':
            if x and y and color :
                div = plot_obj.histogram_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.histogram_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'box_plot':
            if x and y and color :
                div = plot_obj.box_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.box_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'bubble_plot':
            if x and y and color :
                div = plot_obj.bubble_plot(x,y,size,hover_name,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.bubble_plot(x,y,size,hover_name)
                error =False
            else:

                error =True
        elif plot_type == 'pie_chart':
                div = plot_obj.pie_plot(values=values,names=names,legend=legend)
                error =False
        elif plot_type == 'time_series_plot':

            if x and y:
                    div = plot_obj.time_series_plot(x,y)
                    error =False
            else:

                error =True
        elif plot_type == 'heatmap':

                if x and y:
                    div = plot_obj.dencity_heatmap_plot(x,y)
                    error =False
                else:

                    error =True
        elif plot_type == 'count':
            if x and color :
                div = plot_obj.count_plot(x,color=color)
                error =False
            if x :
                div = plot_obj.count_plot(x)
                error =False
            else:
                error =True
        elif plot_type == 'cat':
            #print("x,y,facet_col",x,y,facet_col)
            if x and y and color and facet_col:
                #print("cat with all color call")
                div = plot_obj.cat_plot(x,y,facet_col,color=color)
            elif x and y and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col)

        return div

class QueryPlot:
    def __init__(self,df,pk):
        self.df = df
        self.pk = pk


    def update_plot(self,plot,plot_type,x=None,y=None,z=None,color=None,legend=False,size=None,hover_name=None,values=None,names=None,facet_col=None,orientation='h'):
        #print("heat map",x,y)
        update = Plot.objects.filter(pk=plot.pk).update(plot_type=plot_type,x_axis=x,y_axis=y,z_axis=z,color=color,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
        df = self.df
        plot_obj = PlotRender(df)

        #print("the color in update function is",color)
        if plot_type == 'scatter_2d':
            if x and y and color :
                #print("update the plot ",update)
                div = plot_obj.scatter_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.scatter_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'scatter_3d':
            if x and y and z and color:
                div = plot_obj.scatter_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.scatter_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_3d':
            if x and y and z and color :
                div = plot_obj.line_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.line_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_2d':
            if x and y and color :
                div = plot_obj.line_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.line_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,)
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend)
                error =False
            else:
                error =True

        elif plot_type == 'horizontal_bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,orientation='h')
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend,orientation='h')
                error =False
            else:
                error =True

        elif plot_type == 'histogram':
            if x and y and color :
                div = plot_obj.histogram_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.histogram_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'box_plot':
            if x and y and color :
                div = plot_obj.box_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.box_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'bubble_plot':
            #print("the bubble plot",plot_type,x,y,)
            if x and y and color :
                #print("in side the bubble")
                div = plot_obj.bubble_plot(x,y,size,hover_name,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.bubble_plot(x,y,size,hover_name)
                error =False
            else:

                error =True
        elif plot_type == 'pie_chart':
                div = plot_obj.pie_plot(values=values,names=names,legend=legend)
                error =False
        elif plot_type == 'time_series_plot':

            if x and y:
                    div = plot_obj.time_series_plot(x,y)
                    error =False
            else:

                error =True
        elif plot_type == 'heatmap':

                if x and y:
                    div = plot_obj.dencity_heatmap_plot(x,y)
                    error =False
                else:

                    error =True
        elif plot_type == 'count':
            if x and color :
                div = plot_obj.count_plot(x,color=color)
                error =False
            if x :
                div = plot_obj.count_plot(x)
                error =False
            else:
                error =True
        elif plot_type == 'cat':
            if x and y and color and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col,color=color)
            elif x and y and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col)


        return div

    def create_plot(self,plot_type,x=None,y=None,z=None,color=None,legend=False,size=None,hover_name=None,values=None,names=None,facet_col=None,orientation='h'):
        #print("the facet_col",facet_col)
        plot = Plot.objects.create(plot_type=plot_type,x_axis=x,y_axis=y,z_axis=z,size=size,color=color,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)

        df = self.df
        pk = self.pk
        update = ProjectQuery.objects.filter(pk=pk).update(plot=plot)
        plot_obj = PlotRender(df)
        if plot_type == 'scatter_2d':
            if x and y and color :
                div = plot_obj.scatter_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.scatter_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'scatter_3d':
            if x and y and z and color:
                div = plot_obj.scatter_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.scatter_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_3d':
            if x and y and z and color :
                div = plot_obj.line_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.line_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_2d':
            if x and y and color :
                div = plot_obj.line_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.line_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend)
                error =False
            else:
                error =True
        elif plot_type == 'horizontal_bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,orientation='h')
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend,orientation='h')
                error =False
            else:
                error =True
        elif plot_type == 'histogram':
            if x and y and color :
                div = plot_obj.histogram_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.histogram_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'box_plot':
            if x and y and color :
                div = plot_obj.box_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.box_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'bubble_plot':
            if x and y and color :
                div = plot_obj.bubble_plot(x,y,size,hover_name,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.bubble_plot(x,y,size,hover_name)
                error =False
            else:

                error =True
        elif plot_type == 'pie_chart':
                div = plot_obj.pie_plot(values=values,names=names,legend=legend)
                error =False
        elif plot_type == 'time_series_plot':

            if x and y:
                    div = plot_obj.time_series_plot(x,y)
                    error =False
            else:

                error =True
        elif plot_type == 'heatmap':

                if x and y:
                    div = plot_obj.dencity_heatmap_plot(x,y)
                    error =False
                else:

                    error =True
        elif plot_type == 'count':
            if x and color :
                div = plot_obj.count_plot(x,color=color)
                error =False
            if x :
                div = plot_obj.count_plot(x)
                error =False
            else:
                error =True
        elif plot_type == 'cat':
            if x and y and color and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col,color=color)
            elif x and y and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col)

        return div


    def plot(self,plot):
        df = self.df
        x=plot.x_axis
        y=plot.y_axis
        z=plot.z_axis
        color=plot.color
        legend= plot.legend
        values= plot.values
        names=plot.names
        orientation = plot.orientation
        size=plot.size
        hover_name = plot.hover_name
        plot_type =plot.plot_type
        facet_col = plot.facet_col
        plot_obj = PlotRender(df)
        if plot_type == 'scatter_2d':
            if x and y and color :
                div = plot_obj.scatter_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.scatter_plot(x,y)
                error =False
            else:
                error =True
        elif plot_type == 'scatter_3d':
            if x and y and z and color:
                div = plot_obj.scatter_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.scatter_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_3d':
            if x and y and z and color :
                div = plot_obj.line_plot_3d(x,y,z,color=color,legend=legend)
                error =False
            elif x and y and z:
                div = plot_obj.line_plot_3d(x,y,z)
                error =False
            else:
                error =True

        elif plot_type == 'line_2d':
            if x and y and color :
                div = plot_obj.line_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.line_plot(x,y)
                error =False
            else:
                error =True

        elif plot_type == 'horizontal_bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend,orientation='h')
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend,orientation='h')
                error =False
            else:
                error =True
        elif plot_type == 'bar':
            if x and y  and color:
                div = plot_obj.bar_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y :
                div = plot_obj.bar_plot(x,y,legend=legend)
                error =False
            else:
                error =True
        elif plot_type == 'histogram':
            if x and y and color :
                div = plot_obj.histogram_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.histogram_plot(x,y)
                error =False
            else:

                error =True
        elif plot_type == 'box_plot':
            if x and y and color :
                div = plot_obj.box_plot(x,y,color=color,legend=legend)
                error =False
            elif x and y:
                div = plot_obj.box_plot(x,y)
                error =False
            else:

                error =True

        elif plot_type == 'bubble_plot':
            #print("the plot")
            if x and y and color :
                #print("bubble plot")
                div = plot_obj.bubble_plot(x,y,size,hover_name,color=color,legend=legend)
                error =False
            elif x and y:
                #print("bubble plot")
                div = plot_obj.bubble_plot(x,y,size,hover_name)
                error =False
            else:
                #print("else bubble plot")
                error =True
        elif plot_type == 'pie_chart':
                div = plot_obj.pie_plot(values=values,names=names,legend=legend)
                error =False
        elif plot_type == 'time_series_plot':

            if x and y:
                    div = plot_obj.time_series_plot(x,y)
                    error =False
            else:

                error =True
        elif plot_type == 'heatmap':

                if x and y:
                    div = plot_obj.dencity_heatmap_plot(x,y)
                    error =False
                else:

                    error =True
        elif plot_type == 'count':
            if x and color :
                div = plot_obj.count_plot(x,color=color)
                error =False
            if x :
                div = plot_obj.count_plot(x)
                error =False
            else:
                error =True
        elif plot_type == 'cat':
            if x and y and color and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col,color=color)
            elif x and y and facet_col:
                div = plot_obj.cat_plot(x,y,facet_col)

        return div
