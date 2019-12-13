from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from wrw.models import Symptom, Method, UserMethodTrialStart
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class MethodPage(View):
    template_name = 'pages/method.html'

    def getStatisticsData(self, scores):
        y_values = [0, 0, 0, 0, 0]
        x_values = ['|-100 ~ -61|', '|-60 ~ -21|',
                    '|-20 ~ 20|', '|21 ~ 60|', '|61 ~ 100|']

        for score in scores:
            if score < -60:
                y_values[0] += 1
            elif score < -20:
                y_values[1] += 1
            elif score <= 20:
                y_values[2] += 1
            elif score <= 60:
                y_values[3] += 1
            else:
                y_values[4] += 1

        return dict(x=x_values, y=y_values)

    def getStatisticsChart(self, symptom_severity_scores=[], side_effect_severity_scores=[]):
        fig = make_subplots(rows=1, cols=2, subplot_titles=[
            'Symptom Severity', 'Side Effect Severity'])

        width = [0.5 for i in range(5)]

        max_value = 0
        for index, scores in enumerate([symptom_severity_scores, side_effect_severity_scores]):
            y_values = [0, 0, 0, 0, 0]
            x_values = ['|-100 ~ -61|', '|-60 ~ -21|',
                        '|-20 ~ 20|', '|21 ~ 60|', '|61 ~ 100|']

            for score in scores:
                if score < -60:
                    y_values[0] += 1
                elif score < -20:
                    y_values[1] += 1
                elif score <= 20:
                    y_values[2] += 1
                elif score <= 60:
                    y_values[3] += 1
                else:
                    y_values[4] += 1

            max_value = max(y_values+[max_value])
            max_value += 3 if max_value % 2 else 2

            fig.add_trace(
                go.Bar(x=x_values, y=y_values, hoverinfo='skip', width=width, marker_color='#8BC8DB'), row=1, col=(index+1))

            fig.add_layout_image(
                dict(
                    source="/static/images/MiserableFace.png",
                    xref="paper", yref="paper",
                    x=0+(index)*0.55, y=0,
                    sizex=0.5, sizey=0.5
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/SadFace.png",
                    xref="paper", yref="paper",
                    x=0.09+(index)*0.55, y=0,
                    sizex=0.5, sizey=0.5
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/NeutralFace.png",
                    xref="paper", yref="paper",
                    x=0.18+(index)*0.55, y=0,
                    sizex=0.5, sizey=0.5
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/HappyFace.png",
                    xref="paper", yref="paper",
                    x=0.27+(index)*0.55, y=0,
                    sizex=0.5, sizey=0.5
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/EcstaticFace.png",
                    xref="paper", yref="paper",
                    x=0.36+(index)*0.55, y=0,
                    sizex=0.5, sizey=0.5
                ))

        fig.update_layout(height=250, margin=dict(b=20, t=20, r=20, l=20),
                          showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, title_text='Scores')
        fig.update_yaxes(showticklabels=True, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, autorange=False, range=[0, max_value], title_text='# of Users')

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,
                        config=dict(displayModeBar=False))

        return plot_div

    def getSeverityTimelineChart(self, user, method, severities_data=[], height=250):
        sizes = [10] * len(severities_data)
        line_colors = ['rgba(99, 110, 250, 0)'] * len(severities_data)

        fig = go.Figure()

        umts = UserMethodTrialStart.objects.get(user=user, method=method)

        fig.add_shape(
            x0=umts.getStartedAt(), x1=umts.getEndedAt(timezone.now()),
            y0=0, y1=1, line=dict(width=0), type="rect", xref="x", yref="paper", opacity=0.2, fillcolor="yellow")

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

    def get(self, request, *args, **kwargs):
        symptom_id = kwargs['symptom_id'] if 'symptom_id' in kwargs else None
        method_id = kwargs['method_id'] if 'method_id' in kwargs else None

        if symptom_id is None or method_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        symptom = Symptom.objects.get(id=symptom_id)
        method = Method.objects.get(id=method_id)

        symptom_severity_scores = method.getSymptomScores(symptom)
        side_effect_severity_scores = method.getSideEffectScores(symptom)

        statisctics_charts = self.getStatisticsChart(
            symptom_severity_scores, side_effect_severity_scores)

        user_timelines = [dict(
            user=user,
            chart=self.getSeverityTimelineChart(
                user, method,
                user.getSymptomSeverities(symptom))
        ) for user in method.getUsersHaveSymptom(symptom)]

        return render(request, self.template_name, dict(
            symptom=symptom,
            method=method,
            statisctics_charts=statisctics_charts,
            user_timelines=user_timelines
        ))
