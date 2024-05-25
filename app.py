import streamlit as st
from streamlit_login_auth_ui.widgets import __login__

# Create the login widget and check if the user is logged in
__login__obj = __login__(auth_token="pk_prod_A31TYCQCX6M1VEKYG3009SN342HY",
                        company_name="Image_based_search",
                        width=200, height=250,
                        logout_button_name='Logout', hide_menu_bool=False,
                        hide_footer_bool=False,
                        lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN = __login__obj.build_login_ui()
username = __login__obj.get_username()

if LOGGED_IN:
      
      st.markdown(f"<p style='color: red;'>Welcome, {username}!</p>", unsafe_allow_html=True)

      # Import and call the main function from mainapp.py
      import mainapp
      mainapp.main()



