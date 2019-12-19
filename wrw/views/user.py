from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from wrw.models import User, Method, UserSymptomUpdate, UserMethodTrialStart, Symptom
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
from random import randrange
import colorlover


class UserPage(View):
    template_name = 'pages/user.html'

    def getTreatmentGanttChart(self, user):
        symptoms = user.getSymptoms()
        methods = []
        for symptom in symptoms:
            methods += user.getMethodsBySymptom(symptom)

        methods = list(dict.fromkeys(methods))

        if not symptoms:
            return ''

        dataframe = []
        treatment_timelines = []
        for method in methods:
            user_method_trial_starts = UserMethodTrialStart.objects.filter(
                user=user, method=method).order_by('created_at')

            user_symptom_updates = []
            started_at = user_method_trial_starts.first().getStartedAt()
            ended_at = user_method_trial_starts.last().getEndedAt()

            if ended_at is None:
                ended_at = timezone.now() + timedelta(days=1)

            started_at = datetime.combine(started_at, datetime.min.time())
            ended_at = datetime.combine(ended_at, datetime.min.time())

            user_symptom_updates += UserSymptomUpdate.objects.filter(
                user_symptom__user=user, created_at__range=[started_at, ended_at])

            if user_symptom_updates:
                user_symptom_updates.sort(key=lambda x: x.getCreatedAt())

                annotation_at = started_at+(ended_at-started_at)/2

                treatment_timelines.append(dict(
                    dict(
                        method=str(method),
                        started_at=started_at,
                        ended_at=ended_at,
                        annotation_at=annotation_at
                    )
                ))

        dataframe += [dict(
            Task=treatment_timeline['method'],
            Start=treatment_timeline['started_at'],
            Finish=treatment_timeline['ended_at']
        ) for treatment_timeline in reversed(treatment_timelines)]

        dataframe.append(dict(
            Task='',
            Start=datetime.today(),
            Finish=datetime.today()
        ))

        if not dataframe:
            return ''

        # figure
        fig = ff.create_gantt(dataframe, bar_width=0.45,
                              title=None, group_tasks=False)

        # hide hover text
        for index in range(len(fig['data'])):
            fig['data'][index].update(hoverinfo='skip')

        # show method at the middle of the bar
        annotations = [dict(
            x=treatment_timeline['annotation_at'],
            y=index,
            showarrow=False,
            text='<b>%s</b>' % treatment_timeline['method'],
            font=dict(color='black', size=12)
        ) for index, treatment_timeline in enumerate(reversed(treatment_timelines))]

        # plot figure
        fig['layout']['annotations'] = annotations
        fig.update_layout(height=350, margin=dict(b=20, t=20, r=180, l=60),
                          showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,
                        config=dict(displayModeBar=False))

        return plot_div

    def getSeverityTimelines(self, user):
        symptoms = user.getSymptoms()

        severity_dict_list = []

        severity_dict_list.append(
            dict(name="Side Effect", data=user.getSideEffectSeverities()))

        for symptom in symptoms:
            severity_dict_list.append(
                dict(name=symptom.name, data=user.getSymptomSeverities(symptom)))

        colors = colorlover.scales['10']['qual']['Paired']
        colors = ['255, 0, 0'] + [text[4:-2] for text in colors]
        if len(severity_dict_list):
            fig = go.Figure()

            for index, severity_dict in enumerate(severity_dict_list):
                item_list = severity_dict['data']

                sizes = [10] * len(item_list)

                line_colors = ['rgba(%s, 0)' % colors[index]] * len(item_list)
                fig.add_trace(go.Scatter(x=[item['created_at'] for item in item_list],
                                         y=[item['severity']
                                            for item in item_list],
                                         hoverinfo='text',
                                         hovertext=[item['title']
                                                    for item in item_list],
                                         mode='lines+markers',
                                         marker=dict(size=sizes, opacity=1, color='rgb(%s)' % colors[index], line=dict(
                                             width=12, color=line_colors)),
                                         line_color='rgb(%s)' % colors[index],
                                         customdata=item_list,
                                         name=severity_dict['name']))

            fig.add_trace(go.Scatter(x=[datetime.today()],
                                     y=[0],
                                     hoverinfo='none',
                                     mode='markers',
                                     marker=dict(size=sizes, opacity=0, line=dict(width=0))))
            fig.add_layout_image(
                dict(
                    source="/static/images/MiserableFace.png",
                    xref="paper", yref="paper",
                    x=-0.05, y=0.9,
                    sizex=0.15, sizey=0.15
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/SadFace.png",
                    xref="paper", yref="paper",
                    x=-0.05, y=0.7,
                    sizex=0.15, sizey=0.15
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/NeutralFace.png",
                    xref="paper", yref="paper",
                    x=-0.05, y=0.5,
                    sizex=0.15, sizey=0.15
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/HappyFace.png",
                    xref="paper", yref="paper",
                    x=-0.05, y=0.3,
                    sizex=0.15, sizey=0.15
                ))
            fig.add_layout_image(
                dict(
                    source="/static/images/EcstaticFace.png",
                    xref="paper", yref="paper",
                    x=-0.05, y=0.1,
                    sizex=0.15, sizey=0.15
                ))

            fig.update_layout(height=250, margin=dict(b=20, t=20, r=180, l=60), showlegend=True,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode='closest')
            fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                             showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)
            fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=True,
                             showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, autorange=False, range=[0, 5])

            return plot(fig, output_type='div', include_plotlyjs=False,
                        config=dict(displayModeBar=False))

        return ''

    def get(self, request, *args, **kwargs):
        user_id = kwargs['user_id'] if 'user_id' in kwargs else None

        if user_id is None:
            return HttpResponse('Provided Parameter is invalid.')

        try:
            user = User.objects.get(id=user_id)
        except:
            return HttpResponse('No user.')

        symptoms = user.getSymptoms()

        is_no_symptom = False if len(symptoms) > 0 else True

        treatments = Method.objects.all()
        is_no_treatment = is_no_symptom or (
            False if len(treatments) > 0 else True)

        is_no_user_symptom = is_no_symptom or (
            False if len(user.getSymptoms()) > 0 else True)

        treatment_timeline_chart = self.getTreatmentGanttChart(user)
        severity_timelines = self.getSeverityTimelines(user)

        return render(request, self.template_name, dict(
            user=user,
            is_no_symptom=False,
            is_no_treatment=is_no_treatment,
            is_no_user_symptom=is_no_user_symptom,
            symptoms=Symptom.objects.all(),
            treatment_timeline_chart=treatment_timeline_chart,
            severity_timelines=severity_timelines
        ))
