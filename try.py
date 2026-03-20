import dash
from dash import dcc, html, Input, Output, State, ALL
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)
server = app.server

# File paths
file_path = "users.csv"
admin_path = "admin.csv"

# Ensure CSVs exist
if not os.path.exists(file_path):
    pd.DataFrame(columns=['Name','Passing Year','Aquired Skill','Enter Collage','Year of Experience','Quiz Score','Score']).to_csv(file_path, index=False)

if not os.path.exists(admin_path):
    pd.DataFrame(columns=['Required Skills']).to_csv(admin_path,index=False)

# Load data
show_df = pd.read_csv(file_path)
soham_df3 = pd.read_csv(admin_path)

# Normalize columns
show_df.columns = show_df.columns.str.strip()
show_df['Name'] = show_df['Name'].str.strip()
show_df['Aquired Skill'] = show_df['Aquired Skill'].apply(lambda x: x if isinstance(x, list) else str(x).split(','))

soham_df3.columns = soham_df3.columns.str.strip()
if 'Required Skills' in soham_df3.columns:
    soham_df3['Required Skills'] = soham_df3['Required Skills'].apply(lambda x: x if isinstance(x, list) else str(x).split(','))

# Convert numeric fields
show_df['Year of Experience'] = pd.to_numeric(show_df.get('Year of Experience',0), errors='coerce').fillna(0)
show_df['Quiz Score'] = pd.to_numeric(show_df.get('Quiz Score',0), errors='coerce').fillna(0)

# Function to create quiz pie chart
def quiz_pie_chart(score):
    fig = go.Figure(go.Pie(
        values=[score, 3-score],
        labels=['Scored','Remaining'],
        hole=0.6,
        marker_colors=['#00cc96', '#e9ecef'],
        textinfo='none'
    ))
    fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), height=150, width=150)
    return fig

# Questions
questions = [
    {"id": "q1", "question": "NumPy: What does np.array() do?", "options": ["Creates list","Creates array","Sorts data"], "answer": "Creates array"},
    {"id": "q2", "question": "Pandas: What is a DataFrame?", "options": ["1D array","2D tabular structure","Graph"], "answer": "2D tabular structure"},
    {"id": "q3", "question": "Dash: What is it used for?", "options": ["Game dev","Web dashboards","Database"], "answer": "Web dashboards"}
]

def generate_questions():
    return [
        html.Div([
            html.P(q["question"]),
            dcc.RadioItems(
                id={"type":"question","index":q["id"]},
                options=[{"label":opt,"value":opt} for opt in q["options"]],
            )
        ]) for q in questions
    ]

# Layout
app.layout = html.Div([
    html.H2("Candidate Dashboard"),
    dcc.Dropdown(
        placeholder="Select Name",
        id="name_info",
        options=[{'label':k,'value':k} for k in show_df['Name']]
    ),
    html.Div(id="complete_detail")
])

# Callback to show student info safely
@app.callback(
    Output('complete_detail','children'),
    Input('name_info','value')
)
def info(selected_name):
    if not selected_name:
        return html.Div("Select a candidate")
    
    filtered = show_df[show_df['Name'] == selected_name]
    if filtered.empty:
        return html.Div(f"No data found for '{selected_name}'")
    
    row = filtered.iloc[0]
    
    return html.Div([
        html.H4(row['Name']),
        html.P(f"Passing Year: {row['Passing Year']}"),
        html.P(f"Acquired Skill: {row['Aquired Skill']}"),
        dcc.Graph(figure=quiz_pie_chart(row['Quiz Score'])),
        html.P(f"Performance: {row.get('Performance','N/A')}")
    ], style={
        'border':'1px solid #ccc',
        'padding':'15px',
        'margin':'10px',
        'borderRadius':'10px',
        'width':'200px',
        'display':'inline-block',
        'textAlign':'center',
        'boxShadow':'2px 2px 5px #aaa'
    })

if __name__ == "__main__":
    app.run(debug=True)