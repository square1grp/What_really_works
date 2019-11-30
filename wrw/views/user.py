from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from wrw.models import User, Method
from plotly.offline import plot
import plotly.graph_objects as go


class UserPage(View):
    template_name = 'pages/user.html'

    def getSeverityTimelineChart(self, severities_data=[], height=250):
        sizes = [10] * len(severities_data)
        line_colors = ['rgba(99, 110, 250, 0)'] * len(severities_data)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[severity_data['created_at'] for severity_data in severities_data],
                                 y=[severity_data['severity']
                                     for severity_data in severities_data],
                                 hoverinfo='text',
                                 hovertext=[severity_data['title']
                                            for severity_data in severities_data],
                                 mode='lines+markers',
                                 marker=dict(size=sizes, opacity=1, color='rgb(99, 110, 250)', line=dict(
                                     width=12, color=line_colors)),
                                 customdata=severities_data))

        fig.update_layout(height=height, margin=dict(b=20, t=20, r=20, l=20), showlegend=False,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode='closest')
        fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, autorange=False, range=[0, 5], title_text='Severity')

        return plot(fig, output_type='div', include_plotlyjs=False,
                    config=dict(displayModeBar=False))

    def getSideEffectTimelineChart(self, user):
        severities_data = user.getSideEffectSeverities()

        return self.getSeverityTimelineChart(severities_data)

    def getSymptomTimelineChart(self, user, symptom):
        severities_data = user.getSymptomSeverities(symptom)

        return self.getSeverityTimelineChart(severities_data)

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        user = User.objects.get(id=user_id)

        symptoms = user.getSymptoms()

        is_no_symptom = False if len(symptoms) > 0 else True

        treatments = Method.objects.all()
        is_no_treatment = is_no_symptom or (
            False if len(treatments) > 0 else True)

        is_no_user_symptom = is_no_symptom or (
            False if len(user.getSymptoms()) > 0 else True)

        side_effect_timeline_chart = self.getSideEffectTimelineChart(user)
        symptom_timelines = [dict(
            symptom=symptom,
            chart=self.getSymptomTimelineChart(user, symptom)
        ) for symptom in symptoms]

        return render(request, self.template_name, dict(
            user=user,
            is_no_symptom=False,
            is_no_treatment=is_no_treatment,
            is_no_user_symptom=is_no_user_symptom,
            symptoms=symptoms,
            treatment_timeline=None,
            side_effect_timeline_chart=side_effect_timeline_chart,
            symptom_timelines=symptom_timelines
        ))
