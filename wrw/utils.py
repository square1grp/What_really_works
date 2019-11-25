from .models import *
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime
import pytz


# get all users by symptom
def getUsersBySymptom(symptom, no_duplicate=True):
    symptom = Symptom.objects.get(
        id=symptom) if isinstance(symptom, int) else symptom
    users = [user_symptom.user for user_symptom in UserSymptom.objects.filter(
        symptom=symptom)]

    users = list(dict.fromkeys(users)) if no_duplicate else users

    return users


# add user symptom
def addUserSymptom(params):
    user = User.objects.get(id=params['user_id'])
    symptom = Symptom.objects.get(id=params['symptom_id'])
    created_at = datetime.strptime(
        params['created_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC')).date()

    try:
        user_symptom = UserSymptom(
            user=user, symptom=symptom, created_at=created_at)
        user_symptom.save()
    except:
        pass


# update user symptom
def updateUserSymptom(params):
    import pdb; pdb.set_trace()
    method = Method.objects.get(id=params['method_id'])
    start_drawback = Drawback.objects.get(id=params['start_drawback_id'])
    started_at = datetime.strptime(
        params['started_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC')).date()

    user_method_trial_start = UserMethodTrialStart(
        method=method, drawback=start_drawback, created_at=started_at)
    user_method_trial_start.save()

    start_severity = Severity.objects.get(id=params['start_severity_id'])

    user_symptom_trial_start = UserSymptomTrialStart(
        user_method_trial_start=user_method_trial_start, severity=start_severity)
    user_symptom_trial_start.save()

    user_symptom = UserSymptom.objects.get(id=params['user_symptom_id'])
    user_symptom.user_symptom_trial_start = user_symptom_trial_start

    if 'ended_treatment' in params and params['ended_treatment'] == 'on':
        end_drawback = Drawback.objects.get(id=params['end_drawback_id'])
        end_severity = Severity.objects.get(id=params['end_severity_id'])
        ended_at = datetime.strptime(
            params['ended_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC')).date()

        user_method_trial_end = UserMethodTrialEnd(user_method_trial_start=user_method_trial_start, drawback=end_drawback, created_at=ended_at)
        user_method_trial_end.save()

        user_symptom_trial_end = UserSymptomTrialEnd(
            user_symptom_trial_start=user_symptom_trial_start, user_method_trial_end=user_method_trial_end, severity=end_severity)
        user_symptom_trial_end.save()

        user_symptom.user_symptom_trial_end = user_symptom_trial_end

    user_symptom.save()


# add user symptom update
def addUserSymptomUpdate(params):
    user_symptom = UserSymptom.objects.get(id=params['user_symptom_id'])
    severity = Severity.objects.get(id=params['severity_id'])
    drawback = Drawback.objects.get(id=params['drawback_id'])
    title = params['title']
    description = params['description']
    created_at = datetime.strptime(
        params['created_at'], '%m/%d/%Y').astimezone(pytz.timezone('UTC')).date()

    try:
        user_symptom_update = UserSymptomUpdate(user_symptom=user_symptom, severity=severity,
                                                drawback=drawback, title=title, description=description, created_at=created_at)
        print(user_symptom_update)
        user_symptom_update.save()
    except:
        pass


# get statistics x, y values
def getStatisticsData(score_list, is_drawback=False):
    y_values = [0, 0, 0, 0, 0]
    x_values = ['|-100 ~ -61|', '|-60 ~ -21|',
                '|-20 ~ 20|', '|21 ~ 60|', '|61 ~ 100|']

    for score in score_list:
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


# get statistics chart in method page
def getStatisticsChart(e_statistics_data, d_statistics_data):
    max_value = max(e_statistics_data['y'] + d_statistics_data['y'])
    max_value += 5 if max_value % 2 else 4

    fig = make_subplots(rows=1, cols=2, subplot_titles=[
                        'Effectiveness', 'Drawbacks'])

    width = [0.5 for i in range(5)]
    fig.add_trace(
        go.Bar(x=e_statistics_data['x'], y=e_statistics_data['y'], hoverinfo='skip', width=width), row=1, col=1)
    fig.add_trace(
        go.Bar(x=d_statistics_data['x'], y=d_statistics_data['y'], hoverinfo='skip', width=width), row=1, col=2)

    fig.update_traces(marker_color='#8BC8DB')
    fig.update_layout(height=200, margin=dict(b=20, t=20, r=20, l=20),
                      showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                     showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, title_text='score')
    fig.update_yaxes(showticklabels=True, showgrid=False, zeroline=True,
                     showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, autorange=False, range=[0, max_value], title_text='# of users')

    plot_div = plot(fig, output_type='div', include_plotlyjs=False,
                    config=dict(displayModeBar=False))

    return plot_div


# get treatment gantt chart
def getTreatmentGanttChart(treatment_trials):
    if not treatment_trials:
        return ''

    dataframe = []

    dataframe += [dict(
        Task=treatment_trial['symptom'],
        Start=treatment_trial['started_at'],
        Finish=treatment_trial['ended_at']
    ) for treatment_trial in reversed(treatment_trials)]

    # figure
    fig = ff.create_gantt(dataframe, bar_width=0.45,
                          title=None, group_tasks=False)

    # hide hover text
    for index in range(len(fig['data'])):
        fig['data'][index].update(hoverinfo='skip')

    # show method at the middle of the bar
    annotations = [dict(
        x=treatment_trial['annotation_at'],
        y=index,
        showarrow=False,
        text='<b>%s</b>' % treatment_trial['method'],
        font=dict(color='black', size=12)
    ) for index, treatment_trial in enumerate(reversed(treatment_trials))]

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


# get symptom timelines
def getSymptomTimelines(user, symptoms, height=400):
    symptom_timelines = []

    for symptom in symptoms:
        symptom_timeline = dict(symptom=symptom)

        severity_data = user.getAllSeverityUpdatesBySymptom(symptom)

        if len(severity_data['effectivenesses']) or len(severity_data['drawbacks']):
            sizes = [[10] * len(severity_data['effectivenesses']),
                     [10] * len(severity_data['drawbacks'])]
            line_colors = [['rgba(99, 110, 250, 0)'] * len(severity_data['effectivenesses']),
                           ['rgba(239, 85, 59, 0)'] * len(severity_data['drawbacks'])]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[effectiveness['created_at']
                                        for effectiveness in severity_data['effectivenesses']],
                                     y=[effectiveness['severity']
                                        for effectiveness in severity_data['effectivenesses']],
                                     hoverinfo='text',
                                     hovertext=[effectiveness['title']
                                                for effectiveness in severity_data['effectivenesses']],
                                     mode='lines+markers',
                                     marker=dict(size=sizes[0], opacity=1, color='rgb(99, 110, 250)', line=dict(
                                         width=12, color=line_colors[0])),
                                     name='Symptom Severity',
                                     customdata=severity_data['effectivenesses']))

            fig.add_trace(go.Scatter(x=[drawback['created_at']
                                        for drawback in severity_data['drawbacks']],
                                     y=[drawback['severity']
                                        for drawback in severity_data['drawbacks']],
                                     hoverinfo='text',
                                     hovertext=[drawback['title']
                                                for drawback in severity_data['effectivenesses']],
                                     mode='lines+markers',
                                     marker=dict(size=sizes[1], opacity=1, color='rgb(239, 85, 59)', line=dict(
                                         width=12, color=line_colors[1])),
                                     name='Drawbacks',
                                     customdata=severity_data['drawbacks']))

            fig.update_layout(height=height, margin=dict(b=20, t=20, r=20, l=20), showlegend=True,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode='closest')
            fig.update_xaxes(showticklabels=True, showgrid=False, zeroline=True,
                             showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)
            fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=True,
                             showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, autorange=False, range=[0, 5], title_text='Severity')

            symptom_timeline['chart'] = plot(fig, output_type='div', include_plotlyjs=False,
                                             config=dict(displayModeBar=False))
        else:
            symptom_timeline['chart'] = ''

        symptom_timelines.append(symptom_timeline)

    return symptom_timelines
