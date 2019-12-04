from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.utils import timezone
from wrw.models import User, Method, UserSymptomUpdate, UserMethodTrialStart
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.figure_factory as ff


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
                user=user, method=method)

            user_symptom_updates = []
            started_at = user_method_trial_starts.first().getStartedAt()
            ended_at = user_method_trial_starts.last().getEndedAt()

            if ended_at is None:
                ended_at = timezone.now().date()

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
        fig.update_layout(height=350, margin=dict(b=20, t=20, r=20, l=20),
                          showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=True,
                         showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)

        plot_div = plot(fig, output_type='div', include_plotlyjs=False,
                        config=dict(displayModeBar=False))

        return plot_div

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
            treatment_timeline_chart=treatment_timeline_chart,
            side_effect_timeline_chart=side_effect_timeline_chart,
            symptom_timelines=symptom_timelines
        ))
