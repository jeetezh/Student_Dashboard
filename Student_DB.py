import streamlit as st
import pandas as pd
import psycopg2



PASSWORD="Ro0t@123"
PORT="5432"
USER="postgres"
HOST="localhost"
DATABASE_NAME="project"


st.set_page_config(page_title="STUDENT INFO")

#Connecting to database
@st.cache_resource
def create_connection():
    try:
        conn = psycopg2.connect(
        host=HOST,        
        database=DATABASE_NAME,
        user=USER,
        password=PASSWORD,
        port=PORT              # default PostgreSQL port
        )
        print("Connected to DB")
        return conn
    except Exception as e:
        print(e)
    
conn=create_connection()

print(conn)

@st.cache_resource
def create_cursor():
    return conn.cursor()


cur=create_cursor()

# Create a table if not exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        age INT NOT NULL 
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INT PRIMARY KEY,
        physics INT NOT NULL,
        chemistry INT NOT NULL,
        maths INT NOT NULL,
        percent NUMERIC(5, 2), 
        FOREIGN KEY (id) REFERENCES users(id)     
    );
""")
conn.commit() 




#user credential for login
credential={
    "teacher1":"teacher1",
    "teacher2":"teacher2"
}


if "flag" not in st.session_state:
    st.session_state.flag=0

st.sidebar.subheader("LOGIN")

with st.sidebar.form("login"):
    user=st.text_input("Enter username")
    password1=st.text_input("Enter Password",type="password")
    st.form_submit_button("CONFIRM")


    if user in credential:                         #credential verification
        if credential[user]==password1:
            st.sidebar.success("LOGIN SUCCESSFULL")
            st.session_state.flag=1
        else:
            st.sidebar.error("LOGIN failed")


def view_function():                 #function to view data using join
    query1 = """
                      SELECT 
                       u.id AS user_id,
                       u.name,
                       u.age,
                       m.physics,
                       m.chemistry,
                       m.maths,
                       m.percent
                       FROM users u
                       LEFT JOIN
                       marks m
                       ON u.id=m.id
                       ORDER BY user_id;"""
    cur.execute(query1)       #executing left join to get data
    return cur.fetchall()

if st.session_state.flag:
    st.title(" STUDENT DASHBOARD")


    biodata_tab,marks_tab,edit_tab,view_tab,delete_tab=st.tabs(["Biodata","Marks","Edit","View data","Delete"]) 


    with biodata_tab:
        col1,col2=st.columns(2)

        if "total_student" not in st.session_state:
            st.session_state.total_student=0
        with col1:
            st.session_state.total_student = st.number_input("Enter number of student",step=1)

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)     #to align button
            press=st.button("Submit",key="btn1")

        if press:
            st.write(f"You entered {st.session_state.total_student}")

        #dataframe with user input rows
        data = pd.DataFrame({
            "id": ["" for i in range(st.session_state.total_student)],
            "Name": ["" for i in range(st.session_state.total_student)],
            "Age": ["" for i in range(st.session_state.total_student)]
        })
        
        with st.form("biodata"):
            edited_data = st.data_editor(data,hide_index=True)

            form_submit=st.form_submit_button("Submit")

        if form_submit:
            st.success("✅ Data Submitted")
            st.write("Here is your data:")
            st.dataframe(edited_data,hide_index=True)
            #print(edited_data)
            #print(type(edited_data))

            for index, row in edited_data.iterrows():
                try:
                    if row["id"] =="" or row["Name"]=="" or row["Age"]=="":
                        st.error(f"{index+1} Field cannot be Empty")
                    else:
                        cur.execute(
                        "INSERT INTO users (id, name, age) VALUES (%s, %s, %s) ;",  
                        (int(row["id"]), row["Name"], int(row["Age"]))
                        )
                        conn.commit()
                        st.success(f"{row['Name']} is inserted into database✅")
                except psycopg2.errors.UniqueViolation as e:
                    st.error(f"ID {row['id']}already exists in database")
                    conn.rollback() 
                    
                except psycopg2.errors.NotNullViolation as e:
                    st.error(f"Please enter missing parameter")
                    
    with marks_tab:
        col3,col4=st.columns(2)

        if "std_marks" not in st.session_state:
            st.session_state.std_marks=0
        with col3:
            st.session_state.std_marks = st.number_input("Enter number of student",step=1,key="marks_no")

        with col4:
            st.markdown("<br>", unsafe_allow_html=True)       #to align submit button
            press2=st.button("Submit",key="btn3")

        if press2:
            st.write(f"You entered {st.session_state.std_marks}")


        marks_data= pd.DataFrame({                                              #creating a dataframe for total students
            "id": ["" for i in range(st.session_state.std_marks)],
            "physics": ["" for i in range(st.session_state.std_marks)],
            "chemistry": ["" for i in range(st.session_state.std_marks)],
            "maths": ["" for i in range(st.session_state.std_marks)]

        })
        
        with st.form("marks"):
            edited_marks = st.data_editor(marks_data,hide_index=True)

            form_submit=st.form_submit_button("Submit")

        if form_submit:
            st.success("✅ Data Submitted")
            st.write("Here is your data:")
            st.dataframe(edited_marks,hide_index=True)


            for index, mark in edited_marks.iterrows():
                    try: 
                        if mark["id"] =="" or mark["chemistry"]=="" or mark["maths"]=="" or mark["physics"]=="":   #checking for empty 
                            st.error(f"{index+1} Field cannot be Empty")
                        elif int(mark["id"]) >100 or int(mark["chemistry"])>100 or int(mark["maths"])>100 or int(mark["physics"])>100: #checking marks
                                st.error(f"{index+1} Marks cannot be greater then 100")
                        else:

                            cur.execute(
                            "INSERT INTO marks (id, physics,chemistry,maths,percent) VALUES (%s, %s, %s,%s,%s) ;",  
                            (int(mark["id"]), mark["physics"], (mark["chemistry"]),mark["maths"],((int(mark["chemistry"])+int(mark["maths"])+int(mark["physics"]))/3)
                            ))
                            conn.commit()
                            st.success(f"marks of student ID {mark['id']} is inserted into database")
                    except psycopg2.errors.UniqueViolation as e:
                        st.error(f"ID {mark['id']}already exists in database")
                        conn.rollback() 
                        
                    except psycopg2.errors.NotNullViolation as e:
                        st.error(f"Please enter missing parameter")





    with view_tab:
        cur.execute("SELECT COUNT(*) FROM users;")
        rows = cur.fetchall()
        refresh=st.button("Refresh")
        if rows[0][0]:
            result=view_function()
            if refresh:
               result=view_function()
            

            #print(result)
            column1 = ['user_id', 'name', 'age', 'physics', 'chemistry', 'maths', 'percent']
            view_data=pd.DataFrame(result,columns=column1)
            st.dataframe(view_data,hide_index=True)                 
        else:
            st.warning("NO DATA FOUND")
            st.image("source_image\gif_image.gif",width=300)

    with edit_tab:
        cur.execute("SELECT COUNT(*) FROM users;")
        rows1 = cur.fetchall()

        if rows1[0][0]:
            cur.execute("SELECT id FROM users;")
            result3 = cur.fetchall()

            st.session_state.id_list = [i[0] for i in result3]

            if "selected_student" not in st.session_state:
                st.session_state.selected_student = 0
            if "selected_topic" not in st.session_state:
                st.session_state.selected_topic = None
            if "get_data" not in st.session_state:
                st.session_state.get_data = False
            if "field_biodata" not in st.session_state:
                st.session_state.field_biodata = None
            if "field_marks" not in st.session_state:
                st.session_state.field_marks = None
            if "var" not in st.session_state:
                st.session_state.var = False

            if "edit_press1" not in st.session_state:
                st.session_state.edit_press1=False

            if "edit_press2" not in st.session_state:
                st.session_state.edit_press2=False
            

            with st.form("edit1"):
                st.session_state.selected_student = st.selectbox("Select student ID to edit info", st.session_state.id_list)
                st.session_state.selected_topic = st.selectbox("Select what you want to edit", ["biodata", "marks"])
                submit1=st.form_submit_button("Continue")
                if submit1:
                    st.session_state.get_data=True

            if st.session_state.get_data:
                with st.form("edit2"):
                    if st.session_state.selected_topic == "biodata":
                        st.session_state.field_biodata = st.selectbox("Select Info to edit", ["name", "age"])
                    elif st.session_state.selected_topic == "marks":
                        st.session_state.field_marks = st.selectbox("Select subject to edit", ["physics", "chemistry", "maths"])
                    submitted = st.form_submit_button("OK")
                    if submitted:
                        st.session_state.var = True
                col5,col6=st.columns(2)
                if st.session_state.var:
                    if st.session_state.selected_topic=="biodata":
                        query4=f"SELECT {st.session_state.field_biodata} from users WHERE id={st.session_state.selected_student};"
                        cur.execute(query4)
                        result4=cur.fetchone()[0]
                        #print(result4)
                        print("here in biodta")
                        with col5:
                            value=st.text_input(f"The previous data was {result4}, enter new value")                
                        with col6:
                            st.markdown("<br>", unsafe_allow_html=True)
                            press1=st.button("Submit",key="btn4")
                        if press1:
                            st.session_state.edit_press1=True
                        
                        if press1:
                            update_query = f"UPDATE users SET {st.session_state.field_biodata} = %s WHERE id = %s"
                            if st.session_state.field_biodata=="age":
                                value=int(value)
                            cur.execute(update_query, (value, st.session_state.selected_student))
                            conn.commit()
                            st.success("Data updated successfully!")

                            #st.rerun()


                    
                    if st.session_state.selected_topic=="marks":
                        query4=f"SELECT {st.session_state.field_marks} from marks WHERE id={st.session_state.selected_student};"
                        cur.execute(query4)
                        result4=cur.fetchone()[0]
                        #print(result4)
                        print("here in marks")
                        with col5:
                            value=st.text_input(f"The previous data was {result4}, enter new value")
                            
                        with col6:
                            st.markdown("<br>", unsafe_allow_html=True)
                            press2=st.button("Submit",key="btn5")
                        if press2:
                            st.session_state.edit_press2=True

                        if press2:
                            update_query = f"UPDATE marks SET {st.session_state.field_marks} = %s WHERE id = %s"
                            cur.execute(update_query, (int(value), st.session_state.selected_student))
                            conn.commit()
                            st.success("Data updated successfully!")
        else:
            st.warning("NO DATA FOUND")
            st.image("source_image\gif_image.gif",width=300)


    with delete_tab:

        cur.execute("SELECT COUNT(*) FROM users;")
        rows1 = cur.fetchall()

        if rows1[0][0]:
            cur.execute("SELECT id FROM users;")
            result6 = cur.fetchall()

            delete_list = [i[0] for i in result6]

            if "delete_student" not in st.session_state:
                delete_student=0
            with st.form("delete"):
                st.session_state.delete_student = st.selectbox("Select student ID to delete from Database", st.session_state.id_list)
                confirm=st.form_submit_button("CONFIRM")

                if confirm:
                    cur.execute("DELETE FROM marks WHERE id = %s", (st.session_state.delete_student,))   #query to delete from table using id
                    cur.execute("DELETE FROM users WHERE id = %s", (st.session_state.delete_student,))
                    conn.commit()
                    st.success(f"Student with ID {st.session_state.delete_student} has been deleted successfully!")
        else:
            st.warning("NO DATA FOUND")
            st.image("source_image\gif_image.gif",width=300)






                
















                
