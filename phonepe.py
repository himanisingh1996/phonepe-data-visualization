import io
import pandas as pd
import streamlit as st
import ydata_profiling

import json
import os
import pymysql
from sqlalchemy import create_engine 
from tabulate import tabulate
from PIL import Image
import plotly.express as px

from streamlit_player import st_player
from streamlit_pandas_profiling import st_profile_report
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.add_vertical_space import add_vertical_space
 

# Data Prep


# Reading from csv so as to make it work for everyone in streamlit cloud app...
# Otherwise there's another file named Home_with_SQL_Part.py in Miscellaneous directory in this same repo...

agg_trans_df = pd.read_csv(r'Miscellaneous/agg_trans.csv')
agg_user_df = pd.read_csv(r'Miscellaneous/agg_user.csv')
map_trans_df = pd.read_csv(r'Miscellaneous/map_trans.csv')
map_user_df = pd.read_csv(r'Miscellaneous/map_user.csv')
top_trans_dist_df = pd.read_csv(r'Miscellaneous/top_trans_dist.csv')
top_trans_pin_df = pd.read_csv(r'Miscellaneous/top_trans_pin.csv')
top_user_dist_df = pd.read_csv(r'Miscellaneous/top_user_dist.csv')
top_user_pin_df = pd.read_csv(r'Miscellaneous/top_user_pin.csv')


if 'options' not in st.session_state:
    st.session_state['options'] = {
        'Aggregate Transaction': 'agg_trans_df',
        'Aggregate User': 'agg_user_df',
        'Map Transaction': 'map_trans_df',
        'Map User': 'map_user_df',
        'Top Transaction Districtwise': 'top_trans_dist_df',
        'Top Transaction Pincodewise': 'top_trans_pin_df',
        'Top User Districtwise': 'top_user_dist_df',
        'Top User Pincodewise': 'top_user_pin_df'
    }

df_names = [
            var_name for var_name in globals() 
            if isinstance(globals()[var_name], pd.core.frame.DataFrame) and var_name.endswith('_df')
            ]

if 'df_list' not in st.session_state:
    st.session_state['df_list'] = []
    
    for var_name in df_names:
        st.session_state[var_name] = globals()[var_name]
        st.session_state['df_list'].append(var_name)


def year_to_str(df):
    df['Year'] = df["Year"].astype(str)

for df_name in st.session_state['df_list']:
    df = globals()[df_name]
    year_to_str(df)
    globals()[df_name] = df


# App


st.set_page_config(
                    page_title = 'PhonePe Data Visualization', layout = 'wide',
                    page_icon = 'Related Images and Videos/Logo.png'
                    )

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

st.title(':blue[PhonePe Data Visualization]')

add_vertical_space(2)

phonepe_description = """PhonePe has launched PhonePe Pulse, a data analytics platform that provides insights into
                        how Indians are using digital payments. With over 30 crore registered users and 2000 crore 
                        transactions, PhonePe, India's largest digital payments platform with 46% UPI market share,
                        has a unique ring-side view into the Indian digital payments story. Through this app, you 
                        can now easily access and visualize the data provided by PhonePe Pulse, gaining deep 
                        insights and interesting trends into how India transacts with digital payments."""

st.write(phonepe_description)

add_vertical_space(2)

col1, col2, col3 = st.columns(3)

total_reg_users = top_user_dist_df['Registered_users'].sum()
col1.metric(
            label = 'Total Registered Users',
            value = '{:.2f} Cr'.format(total_reg_users/100000000),
            delta = 'Forward Trend'
            )

total_app_opens = map_user_df['App_opens'].sum()
col2.metric(
            label = 'Total App Opens', value = '{:.2f} Cr'.format(total_app_opens/100000000),
            delta = 'Forward Trend'
            )

col3.metric(label = 'Total Transaction Count', value = '2000 Cr +', delta = 'Forward Trend')

style_metric_cards(background_color='200329')

add_vertical_space(2)

col, buff = st.columns([2, 4])

option = col.selectbox(
                        label='Select Dataset',
                        options=list(st.session_state['options'].keys()),
                        key='df'
                        )

tab1, tab2 = st.tabs(['Reports and Dataset', 'Download Dataset'])

with tab1:
    
    column1, column2, buffer = st.columns([2, 2, 4])
    
    show_profile = column1.button(label = 'Show Detailed Report', key = 'show')
    show_df = column2.button(label = 'Show Dataset', key = 'show_df')
    
    if show_profile:
        df_name = st.session_state['options'][option]
        df = globals()[df_name]
        pr = df.profile_report()
        st_profile_report(pr)
        
    if show_df:
        st.experimental_data_editor(
                                    data = globals()[st.session_state['options'][option]],
                                    use_container_width=True
                                    )

with tab2:
    col1, col2, col3 = st.columns(3)
    
    df_name = st.session_state['options'][option]
    df = globals()[df_name]
    
    csv = df.to_csv()
    json = df.to_json(orient ='records')
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, engine ='xlsxwriter', index = False)
    excel_bytes = excel_buffer.getvalue()
    
    col1.download_button(
                         "Download CSV file", data = csv,
                         file_name = f'{option}.csv',
                         mime = 'text/csv', key = 'csv'
                         )
    col2.download_button(
                         "Download JSON file", data = json,
                         file_name = f'{option}.json',
                         mime = 'application/json', key = 'json'
                         )
    col3.download_button("Download Excel file", data = excel_bytes,
                         file_name = f'{option}.xlsx',
                         mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         key = 'excel'
                         )




import streamlit as st
import plotly.express as px
import json
from streamlit_extras.add_vertical_space import add_vertical_space


# Data Prep


agg_trans = st.session_state["agg_trans_df"]
map_trans = st.session_state["map_trans_df"]
map_user = st.session_state["map_user_df"]


#4


user_state = map_user.groupby('State')['Registered_users'].sum().reset_index()

with open(r"Miscellaneous/india_states.json") as f:
    geojson = json.load(f)

if 'geojson' not in st.session_state:
    st.session_state["geojson"] = geojson

user_state_fig = px.choropleth(
                                user_state, geojson = geojson,
                                locations = 'State',
                                featureidkey = 'properties.ST_NM',
                                color='Registered_users', projection = 'orthographic',
                                labels = {'Registered_users': "Registered Users"},
                                color_continuous_scale = 'reds'
                                )

user_state_fig.update_geos(fitbounds='locations', visible=False)
user_state_fig.update_layout(height=600, width=900)  

#1

trans_type_count = agg_trans.groupby('Transaction_type')['Transaction_count'].sum()

total_trans_count = agg_trans['Transaction_count'].sum()

trans_type_perc = round(trans_type_count / total_trans_count * 100, 2).reset_index()

trans_type_fig = px.pie(
                        trans_type_perc, names='Transaction_type',
                        values='Transaction_count', hole=.65,
                        hover_data={'Transaction_count': False}
                        )

trans_type_fig.update_layout(width = 900, height = 500)


#2


trans_state = agg_trans.groupby('State')['Transaction_count'].sum().reset_index()
trans_state_sorted = trans_state.sort_values(by='Transaction_count', ascending=False).head(15)

trans_state_fig = px.bar(
                         trans_state_sorted, x='Transaction_count',
                         y='State', orientation='h',
                         text='Transaction_count', text_auto='.2s',
                         labels = {'Transaction_count': "Transaction Count"}
                         )

trans_state_fig.update_layout(
                                yaxis=dict(autorange="reversed"),
                                width = 900, height = 500
                                )


#3


trans_district = map_trans.groupby(['State', 'District'])[['Transaction_count']].sum().reset_index()

trans_district_sorted = trans_district.sort_values(by='Transaction_count', ascending=False).head(15)

trans_district_fig = px.bar(
                            trans_district_sorted, x='Transaction_count',
                            y='District', orientation='h',
                            text='Transaction_count', text_auto='.2s',
                            labels = {'Transaction_count': "Transaction Count"},
                            hover_name='State',
                            hover_data={'State': False, 'District': True}
                            )

trans_district_fig.update_layout(
                                 yaxis = dict(autorange="reversed"),
                                 width = 900, height = 500
                                 )





# App

add_vertical_space(3)
#4

st.subheader(':blue[Registered User Count by State]')

st.plotly_chart(user_state_fig, use_container_width = True)

#1

st.subheader(":blue[Transaction Breakdown by Type]")

st.plotly_chart(trans_type_fig)

#2

st.subheader(":blue[Transaction Count by State]")

st.plotly_chart(trans_state_fig)

#3

st.subheader(":blue[Transaction Count by District]")

st.plotly_chart(trans_district_fig)



#MySQlConnection
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="123456", 
)

#print(mydb)
mycursor = mydb.cursor(buffered=True)
Engine=create_engine("mysql+pymysql://root:123456@localhost/phonepe_db")
tab1, tab2, tab3 = st.tabs(["Explore Data", "Insights", "About"])
with tab1:
    mycursor.execute("Use Phonepe_db")
    col1,col2,col3=st.columns(3)
    selectbox=col1.selectbox("Type",("Transactions", "Users"))
    year_selectbox=col2.selectbox("2018-2023",("2018", "2019","2020","2021","2022","2023"))
    quarter_selectbox=col3.selectbox("Quarter",("1", "2","3","4"))
    a=int(year_selectbox)
    b=int(quarter_selectbox) 
    if(selectbox=="Transactions"):
        mycursor.execute(f"select sum(count) as Transactions , round(sum(amount)) as Value, round((sum(amount)/sum(count))) as Average from agg_t where year= {a} and quarter={b}")
        out=mycursor.fetchall()
        st.success("Transactions value :{:.2f}".format(out[0][0]))
        st.info("Payment value :{:.2f}".format(out[0][1]))
        st.success("Average Transactions value :{:.2f}".format(out[0][2]))
        col1,col2=st.columns(2)
        mycursor.execute(f"select state, sum(amount) from agg_t where year={a} and quarter={b} group by state")
        out=mycursor.fetchall()
        af=pd.DataFrame(out,columns=["state","Transactions"])
        af["state"]=af["state"].map({"andaman-&-nicobar-islands":"Andaman & Nicobar",
                                       "andhra-pradesh":"Andhra Pradesh",
                                       "arunachal-pradesh":"Arunachal Pradesh",
                                       "assam":"Assam",
                                       "bihar":"Bihar",
                                       "chandigarh":"Chandigarh",
                                       "chhattisgarh":"Chhattisgarh",
                                       "dadra-&-nagar-haveli-&-daman-&-diu":"Dadra and Nagar Haveli and Daman and Diu",
                                       "delhi":"Delhi",
                                       "goa":"Goa",
                                       "gujarat":"Gujarat",
                                       "haryana":"Haryana",
                                       "himachal-pradesh":"Himachal Pradesh",
                                       "jammu-&-kashmir":"Jammu & Kashmir",
                                       "jharkhand":"Jharkhand",
                                       "karnataka":"Karnataka",
                                       "kerala":"Kerala",
                                       "ladakh":"Ladakh",
                                       "lakshadweep":"Lakshadweep",
                                       "madhya-pradesh":"Madhya Pradesh",
                                       "maharashtra":"Maharashtra",
                                       "manipur":"Manipur",
                                       "meghalaya":"Meghalaya",
                                       "mizoram":"Mizoram",
                                       "nagaland":"Nagaland",
                                       "odisha":"Odisha",
                                       "puducherry":"Puducherry",
                                       "punjab":"Punjab",
                                       "rajasthan":"Rajasthan",
                                       "sikkim":"Sikkim",
                                       "tamil-nadu":"Tamil Nadu",
                                       "telangana":"Telangana",
                                       "tripura":"Tripura",
                                       "uttar-pradesh":"Uttar Pradesh",
                                       "uttarakhand":"Uttarakhand",
                                       "west-bengal":"West Bengal",})
        fig = px.choropleth(
            af,
geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='state',
            color='Transactions',
            color_continuous_scale='Blues'
        )
        fig.update_geos(fitbounds="locations", visible=False)
        col1.plotly_chart(fig)
        mycursor.execute(f"select  paymenttype, round(sum(amount)) from agg_t where year={a} and quarter={b} group by paymenttype")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["a","b"])
        fig1=px.pie(values=df["b"],names=df["a"],color_discrete_sequence=px.colors.sequential.RdBu,title="Paymenttype of Selected Year&Quarter")
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        col2.plotly_chart(fig1)
    elif(selectbox=="Users"):
        mycursor.execute(f"select sum(registeredUsers) as registeredUsers,sum(appOpens) as appOpens from agg_u where  year={a} and quarter={b}")
        out=mycursor.fetchall()
        st.success("Registeres Users :{:.2f}".format(out[0][0]))
        st.info("AppOpens :{:.2f}".format(out[0][1]))
        col1,col2=st.columns(2)
        mycursor.execute(f"select district_name, state, registeredUser as ru ,state, appOpens as ao from map_u where  year={a} and quarter= {b} order by registeredUser desc limit 10")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["district","b","registeredUser","state","ao"])
        fig1=px.bar(df,x="district",y="registeredUser",color="registeredUser", title ="Top 10 states users wise")
        col2.plotly_chart(fig1)
        mycursor.execute(f"select state, sum(registeredusers) from agg_u where year={a} and quarter={b} group by state")
        out=mycursor.fetchall()
        af=pd.DataFrame(out,columns=["state","Users"])
        af["state"]=af["state"].map({"andaman-&-nicobar-islands":"Andaman & Nicobar",
                                       "andhra-pradesh":"Andhra Pradesh",
                                       "arunachal-pradesh":"Arunachal Pradesh",
                                       "assam":"Assam",
                                       "bihar":"Bihar",
                                       "chandigarh":"Chandigarh",
                                       "chhattisgarh":"Chhattisgarh",
                                       "dadra-&-nagar-haveli-&-daman-&-diu":"Dadra and Nagar Haveli and Daman and Diu",
                                       "delhi":"Delhi",
                                       "goa":"Goa",
                                       "gujarat":"Gujarat",
                                       "haryana":"Haryana",
                                       "himachal-pradesh":"Himachal Pradesh",
                                       "jammu-&-kashmir":"Jammu & Kashmir",
                                       "jharkhand":"Jharkhand",
                                       "karnataka":"Karnataka",
                                       "kerala":"Kerala",
                                       "ladakh":"Ladakh",
                                       "lakshadweep":"Lakshadweep",
                                       "madhya-pradesh":"Madhya Pradesh",
                                       "maharashtra":"Maharashtra",
                                       "manipur":"Manipur",
                                       "meghalaya":"Meghalaya",
                                       "mizoram":"Mizoram",
                                       "nagaland":"Nagaland",
                                       "odisha":"Odisha",
                                       "puducherry":"Puducherry",
                                       "punjab":"Punjab",
                                       "rajasthan":"Rajasthan",
                                       "sikkim":"Sikkim",
                                       "tamil-nadu":"Tamil Nadu",
                                       "telangana":"Telangana",
                                       "tripura":"Tripura",
                                       "uttar-pradesh":"Uttar Pradesh",
                                       "uttarakhand":"Uttarakhand",
                                       "west-bengal":"West Bengal",})
        fig = px.choropleth(
            af, geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locations='state',
            color='Users',
            color_continuous_scale='Blues'
        )
        fig.update_geos(fitbounds="locations", visible=False)
        col1.plotly_chart(fig)
        mycursor.execute(f"select district_name, state, registeredUser as ru ,state, appOpens as ao from map_u where  year={a} and quarter= {b} order by appOpens desc limit 10")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["district","b","registeredUser","state","ao"])
        fig2=px.bar(df,x="district",y="ao",color="ao",title ="Top 10 states Apps usage wise",)
        st.plotly_chart(fig2)
with tab2:
    mycursor.execute("use phonepe")
    st.subheader("Some intersting facts about Phonepe")
    questions=st.selectbox("Questions: ", ["Please select one",
                                       "The year which has the most no of Transactions?",
                                       "The most prominent paymenttype of Phonepe across years",
                                       "A district who loves the phonepe app the most",
                                       "An effective payment method during the Covid-19 Lockdown period(2019-2020)",
                                       "The Quarter which tops the transaction list very often across years",
                                       "The Quarter which tops the transaction value list very often across years",
                                       "The State which has most the PhonePe Registered users All time",
                                       "The year which recorded most no of Appopens across India",
                                       "The year which recorded highest no of Registered users across India",
                                       "The States which were unaware about Phonepe"])
    if (questions=="Please select one"):
        st.text("Please Choose any one Query")
    elif(questions=="The year which has the most no of Transactions?"):
        mycursor.execute("select year, sum(count) from agg_t group by year")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["Year","Transact"])
        df["Year"]=df["Year"].astype(str)
        fig=px.bar(df,x="Year",y="Transact",color=df["Transact"],labels={"Transact":"Transactions"})
        st.plotly_chart(fig)
        st.success("2023 has the most no of Transactions so far")
    elif(questions=="The most prominent paymenttype of Phonepe across years"):
        mycursor.execute("select paymenttype, sum(amount) from agg_t group by paymenttype")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["Paymenttype","Transactions"])
        fig=px.bar(df,x="Paymenttype",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Peer to Peer payments was the most prominent Paymenttype across people over Years")
    elif(questions=="A district who loves the phonepe app the most"):
        mycursor.execute("select district_name, sum(amount) from map_t group by district_name order by sum(amount) desc limit 5")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["districtname","Transactions"])
        fig=px.bar(df,x="districtname",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("bengularu Urban made the most use of PhonePe very often")
    elif(questions=="An effective payment method during the Covid-19 Lockdown period(2019-2020)"):
        mycursor.execute("select paymenttype, sum(amount) from agg_t where year between 2019 and 2021 group by paymenttype order by sum(amount) desc limit 5")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["paymenttype","Transactions"])
        fig=px.bar(df,x="paymenttype",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Peer to Peer payments was the most prominent Paymenttype during Covid-19")
    elif(questions=="The Quarter which tops the transaction list very often across years"):
        mycursor.execute("select quarter, sum(count) from agg_t group by quarter")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["quarter","Transactions"])
        df["quarter"]=df["quarter"].astype(str)
        fig=px.bar(df,x="quarter",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Third Quarter Tops the Chart with far margin")
    elif(questions=="The Quarter which tops the transaction value list very often across years"):
        mycursor.execute("select quarter, sum(amount) from agg_t group by quarter")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["quarter","Transactions"])
        fig=px.bar(df,x="quarter",y="Transactions",color=df["Transactions"])
        df["quarter"]=df["quarter"].astype(str)
        st.plotly_chart(fig)
        st.success("Third Quarter Tops the Chart with far margin")
    elif(questions=="The State which has most the PhonePe Registered users All time"):
        mycursor.execute("select state, sum(registeredusers) from top_u group by state order by sum(registeredusers) desc limit 5")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["state","Transactions"])
        fig=px.bar(df,x="state",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Maharastra has more phonepe users than other state in INDIA.")
    elif(questions=="The year which recorded most no of Appopens across India"):
        mycursor.execute("select year, sum(appopens) from map_u group by year")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["year","Transactions"])
        df["year"]=df["year"].astype(str)
        fig=px.bar(df,x="year",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Current year(2023) wins the chart with even a quarter less to its tally")
    elif(questions=="The year which recorded highest no of Registered users across India"):
        mycursor.execute("select year, sum(registereduser) from map_u group by year")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["year","Transactions"])
        df["year"]=df["year"].astype(str)
        fig=px.bar(df,x="year",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Year(2022) had more success among other years")
    elif(questions=="The States which were unaware about Phonepe"):
        mycursor.execute("select state, sum(appopens) from map_u group by state order by sum(appopens) limit 5")
        out=mycursor.fetchall()
        df=pd.DataFrame(out,columns=["state","Transactions"])
        fig=px.bar(df,x="state",y="Transactions",color=df["Transactions"])
        st.plotly_chart(fig)
        st.success("Andaman and Lakshadeep island are unfamiliar about Phonepe in INDIA.")
    col1,col2=st.columns(2)
    with col1:
        mycursor.execute("select year,sum(registeredUsers),sum(appOpens) from agg_u group by year")
        out=mycursor.fetchall()
        df=pd.DataFrame(out, columns=["year","registeredUsers","appOpens"])
        fig=px.line(df,x="year",y="registeredUsers",title="Phonepe Users Growth Over the Years")
        st.plotly_chart(fig)
    fig1=px.line(df,x="year",y="appOpens",title="Phonepe Appopens Growth Over the Years")
    col2.plotly_chart(fig1)
with tab3:
     with st.container():        
        st.header("Phonepe Pulse Data Visualization and Exploration: A User-Friendly Tool Using Streamlit and Plotly")
        st.image(Image.open(r"C:\Users\Admin\Desktop\PhonePe\image8.png"),width=700)
        st.subheader("PhonePe Pulse is your window to the world of how India transacts with interesting trends, deep insights and in-depth analysis based on our data put together by the PhonePe team. A live geo visualization dashboard that displays information and insights from the Phonepe pulse and will be able to access the dashboard from a web browser and easily navigate the different visualizations and facts and figures displayed.")
        
    
    
    
        

    