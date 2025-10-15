from flask import Flask, render_template, request
import requests
import pandas as pd
import json
from datetime import date, datetime
import plotly.io as pio
import plotly.express as px


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html', data=data_soccer())


def data_soccer():
    uri = 'https://api.football-data.org/v4/teams/?limit=500'
    headers = {'X-Auth-Token': '963f590057a946a0b7d805f94569c899'}

    response = requests.get(uri, headers=headers)
    data = response.json()
    with open('teams.json', 'w') as teams_data:
        json.dump(data, teams_data, indent=4)

    return data


def team_info(id_team):
    url = f'https://api.football-data.org/v4/teams/{id_team}?limit=500'
    headers = {'X-Auth-Token': '963f590057a946a0b7d805f94569c899'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code == 403:
        return data
    elif response.status_code == 200:
        print("No error here")
        competitions_list = []
        for competition in data['runningCompetitions']:
            competitions_list.append(competition['name'])
        data['runningCompetitions'] = competitions_list
        with open('team_full_data.json', 'w') as teams_data:
            json.dump(data, teams_data, indent=4)
        return data


def player_info(id_team):
    url = f'https://api.football-data.org/v4/persons/{id_team}'
    headers = {'X-Auth-Token': '963f590057a946a0b7d805f94569c899'}
    response = requests.get(url, headers=headers)
    data = response.json()

    born_year = datetime.strptime(data['dateOfBirth'], '%Y-%m-%d')
    born_year = born_year.year
    current_year = date.today().year
    data['age'] = int(current_year) - int(born_year)
    return data


@app.route('/team/<team_id>')  # Learned here.
# app route takes the variable "username" to display it as route.
# From list "usuarios" above
def team_profile(team_id):
    if team_id:
        #  Learned here. If user exists, displays main page.
        teams = team_info(team_id)
        df = pd.DataFrame(teams['squad'])
        print(df)
        df_nation = df.groupby('nationality')['nationality'].count()
        df_nation.name = 'count'  # Rename Series
        df_nation = df_nation.reset_index()

        #  Change column type to datetime
        df['dateOfBirth'] = pd.to_datetime(df['dateOfBirth'])
        # Plot a bar chart
        fig = px.pie(df_nation, values='count',
                     names='nationality',
                     hover_name='nationality',
                     title='Player nationality count',
                     color_discrete_sequence=px.colors.sequential.Viridis)

        #   To get chart as html and display
        plot_html = pio.to_html(fig, full_html=False)
        return render_template('team_info.html',
                               info=team_info(team_id),
                               plot_html=plot_html)
    else:
        # Learned here. If user doesn't exist, displays error page.
        return 'error'


@app.route('/player/<player_id>')
def player_profile(player_id):
    if player_id:
        return render_template('player_info.html',
                               player_data=player_info(player_id))
    else:
        return 'error'


@app.route('/error')
def error():
    return render_template('error.html')


def read_teams():
    file_path = 'teams.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data['teams']


@app.route("/search", methods=['GET', 'POST'])
def search():
    consulta = request.args.get('busqueda')
    with open("teams.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        # Extract the 'teams' list and convert it to a DataFrame
        df = pd.DataFrame(data["teams"])
    resultado = df[df['name'].str.contains(
        consulta, case=False, na=False)]
    return render_template('index.html',
                           data=resultado.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
