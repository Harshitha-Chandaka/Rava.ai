import streamlit as st

st.title("Welcome to BMI Calculator!!")
weight = st.number_input("Enter your weight in kgs:")
height_format = st.radio("Select your height format:",
                    ['cms', 'meters', 'feet'])

if height_format == 'cms':
    height = st.number_input("Enter your height in Cms:")
    try:
        bmi = weight / ((height/100)**2)
    except:
        st.text("Enter some value of height")
    
elif height_format == 'meters':
    height = st.number_input("Enter your height in meters")
    try:
        bmi = weight / (height**2)
    except:
        st.text("Enter some value of height")

elif height_format == 'feet':
    height = st.number_input("Enter your heigth in feet: ")
    try:
        bmi = weight / ((height//3.28)**2)
    except:
        st.text("Enter some value of height")

if st.button("Calculate BMI"):
    st.text("Your BMI Index is {:.2f}".format(bmi))

    if bmi < 16:
        st.error("You are extremly Underweight")
    elif bmi >= 16 and bmi < 18.5:
        st.warning("You are Underweight")
    elif bmi >= 18.5 and bmi < 25:
        st.success("You are Healthy")
    elif bmi >= 25 and bmi <= 30:
        st.warning("You are Overweight")
    else:
        st.error("You are Extreamly Overweight")




