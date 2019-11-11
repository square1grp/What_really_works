from .models import *
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff


# get all users by symptom
def getUsersBySymptom(symptom, no_duplicate=True):
    symptom = Symptom.objects.get(
        id=symptom) if isinstance(symptom, int) else symptom
    users = [user_symptom.user for user_symptom in UserSymptom.objects.filter(
        symptom=symptom)]

    users = list(dict.fromkeys(users)) if no_duplicate else users

    return users


# get statistics x, y values
def getStatisticsData(score_list, is_drawback=False):
    y_values = [0, 0, 0, 0, 0]
    x_values = ['-100 ~ -61', '-60 ~ -21', '-20 ~ 20', '21 ~ 60', '61 ~ 100']

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

    print(x_values, y_values)
    return dict(x=x_values, y=y_values)


# get statistics chart in method page
def getStatisticsChart(e_statistics_data, d_statistics_data):
    max_value = 1 + max(e_statistics_data['y'] + d_statistics_data['y'])

    fig = make_subplots(rows=1, cols=2)

    width = [0.5 for i in range(5)]
    fig.add_trace(
        go.Bar(x=e_statistics_data['x'], y=e_statistics_data['y'], hoverinfo='skip', width=width), row=1, col=1)
    fig.add_trace(
        go.Bar(x=d_statistics_data['x'], y=d_statistics_data['y'], hoverinfo='skip', width=width), row=1, col=2)

    fig.update_traces(marker_color='#8BC8DB')
    fig.update_layout(height=150, margin=dict(b=20, t=20, r=20, l=20),
                      showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=True,
                     showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=True,
                     showline=True, linewidth=5, linecolor='rgba(0,0,0,0.5)', fixedrange=True, autorange=False, range=[0, max_value])

    plot_div = plot(fig, output_type='div', include_plotlyjs=False,
                    config=dict(displayModeBar=False))

    return plot_div


# get treatment gantt chart
def getTreatmentGanttChart(treatment_trials):
    rating_texts = ['None', 'Mild', 'Moderate', 'Severe', 'Very Severe']
    dataframe = []

    dataframe = [
        dict(Task=rating_text, Start=None, Finish=None) for rating_text in reversed(rating_texts)
    ]

    dataframe += [dict(
        Task=treatment_trial['severity'],
        Start=treatment_trial['started_at'],
        Finish=treatment_trial['ended_at'],
    ) for treatment_trial in treatment_trials]

    # figure
    fig = ff.create_gantt(dataframe, bar_width=0.4,
                          title=None, group_tasks=True)

    # hide hover text
    for index in range(len(fig['data'])):
        fig['data'][index].update(hoverinfo='none')

    # show method at the middle of the bar
    annotations = [dict(
        x=treatment_trial['annotation_at'],
        y=rating_texts.index(treatment_trial['severity']),
        showarrow=False,
        text='<b>%s</b>' % treatment_trial['method'],
        font=dict(color='black', size=16)
    ) for index, treatment_trial in enumerate(treatment_trials)]

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
