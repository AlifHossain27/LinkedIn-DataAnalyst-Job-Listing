import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go

# Page Configs
st.set_page_config(page_title="LinkedIn Jobs EDA", page_icon="📊", layout='wide', initial_sidebar_state='expanded')

# Remove Default theme
theme_plotly = None

# CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Criteria variables
sl=[]

# Load data
@st.cache_data
def load_data():
    us = pd.read_csv('linkedin-jobs-usa.csv')
    ca = pd.read_csv('linkedin-jobs-canada.csv')
    all_data = [us, ca]
    df = pd.concat(all_data)
    return df

# Boxplot to show salary data
@st.cache_data
def salary(df):
    #Cleaning salary column as there are null values and stored in string format
    sal=df['salary'].dropna()
    sal= ["".join(s.split()) for s in sal]   # spliting each terms in string to get 
    sal=[s.split("-",1) for s in sal]
    mini=[float(m) for m in (str(s[0]).replace('$','').replace(',','') for s in sal) ]
    maxi=[float(m) for m in (str(s[1]).replace('$','').replace(',','') for s in sal) ] 
    minimum_salary=[ i for i in mini if i>=30000]
    maximum_salary=[ i for i in maxi if i>=30000]
    max_min=pd.DataFrame(data=zip(minimum_salary,maximum_salary),columns=["minimum_salary","maximum_salary"])
    fig = px.box(max_min, title='Comparison between maximum and minimum salary', labels={'value':'Amount', 'variable':'Salary type'}, notched=True, points='all')
    return fig

# Pie chart to show Prefered job type
@st.cache_data
def job_types(df):
    job_type_data=df['onsite_remote'].value_counts().rename_axis('onsite_remote').reset_index(name='count')
    fig = px.pie(job_type_data, values=job_type_data['count'], names=job_type_data['onsite_remote'], title='Prefered Job types', hole=0.5)
    return fig

# Histogram to show daily job posting
@st.cache_data
def job_posting_days(df):
    data = df['posted_date'].astype('datetime64[ns]')
    data = data.dt.day_name().value_counts()
    fig = px.histogram(data, x=data.index, y=data.values, title='Job posting according to days', color_discrete_sequence=["mediumpurple"])
    fig.update_layout(yaxis_title='Job Postings')
    fig.update_layout(xaxis_title='Days')
    return fig

# Bar chart to show top companies with more hirings
@st.cache_data
def companies_with_more_hiring(df, slider):
    company_data = df['company'].value_counts()[:slider].sort_values()
    fig = px.bar(x=company_data.values, y=company_data.index, title=f'Top {slider} Companies with more hiring', orientation='h', text_auto=True)
    fig.update_layout(yaxis_title='Companies')
    fig.update_layout(xaxis_title='Hirings')
    return fig

def criteria(df):
    try:
        d1=(json.loads(i.replace("'",'"')) for i in df)
        for i in d1:
            if "Seniority level" in i.keys():
                sl.extend(i.values())
    except:
        pass

# Histogram to show seniority level expectation
@st.cache_data
def seniority_level(df):
    json_format = df['criteria'].apply(lambda x: x[1:-1].split(',',3)).to_list()
    for i in json_format:
        criteria(i)
    Seniority_level = pd.Series(sl)
    seniority_data = Seniority_level.value_counts().sort_values(ascending=True)
    fig = px.histogram(x=seniority_data.values, y=seniority_data.index, title='Jobs Based On Seniority Expectaions', color_discrete_sequence=["limegreen"], orientation='h', text_auto=True)
    fig.update_layout(yaxis_title='Seniority')
    fig.update_layout(xaxis_title='Expectations')
    return fig


if __name__ == "__main__":
    # Getting data
    data = load_data()
    
    # Side bar
    st.sidebar.markdown('''
    # Configurations
    ---
    ''')
    st.sidebar.subheader("Top Companies")
    companies_slider = st.sidebar.slider("Number of Companies: ", 2, 15, 5)
    st.sidebar.markdown('''
    ---
    Created by [Alif Hossain Sajib](https://github.com/AlifHossain27)
    ''')
    
    # Home page
    st.header('LinkedIn Data Analyst job listing EDA')
    col1, col2 = st.columns((4,6))
    with col1:
        st.plotly_chart(job_types(data), use_container_width=True)
    with col2:
        st.plotly_chart(salary(data), use_container_width=True)
    st.plotly_chart(companies_with_more_hiring(data, companies_slider), use_container_width=True, height=1200)
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(job_posting_days(data), use_container_width=True)
    with col4:
        st.plotly_chart(seniority_level(data), use_container_width=True)