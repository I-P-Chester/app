###-Preliminaries ----------------------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
#from PIL import Image
#st.set_page_config(layout="wide")

###-"Should I pay off my student loan?"---------------------------------------------------------------------------
st.title("Should I pay off my student loan?")
st.sidebar.title("Should I pay off my student loan?")

##-"About this calculator"---------------------------------------------------------------------------------------
st.subheader("About this calculator")
st.sidebar.subheader("About this calculator")
st.write("""
         This student loan repayment calculator shows your repayments based on your current
         salary and your student loan's repayment threshold. In addition your takehome pay is
         calculated based on your: income tax, national insurance and of course loan repayments.
         """)
         
link = '[Student Loans Company](https://www.gov.uk/government/organisations/student-loans-company)'
link_2 = '[website](https://www.gov.uk/repaying-your-student-loan/what-you-pay) '
st.write(f"""
         Student loan repayments in the UK are determined by the {link}. For more information
         on repayments please visit the "Repaying your student loan" Gov {link_2}.
         """)

#
with st.expander("Disclaimer"):
    st.write("""
             This tool does not constitute financial advice. You should always seek advice from a
             professional when making financial decisions. This calculator is a work in progress.
             I do not recommend taking actions based on the results of this tool; always do your own
             research first, and check a trusted source such as the UK Government website. Note
             that the tool makes many assumptions and so the results could be inaccurate; for
             example, Government policy could change and so the assumptions in the tool may become
             outdated. At the moment the calculator only works for student loans for Scottish,
             English, and Welsh students, and does not function for the self-employed. The
             calculator also does not apply to loans which were taken out before 1998.
             """)
             
##-"Your Details" -------------------------------------------------------------------------------------------------
st.subheader("Your Details")
st.sidebar.subheader("Your Details")
#st.sidebar.markdown("Annual salary")
#st.sidebar.markdown("Debt")
#st.sidebar.markdown("Loan type") 

salary = st.slider("What's your annual salary before tax?", 1000, 200000)
monthly_salary = int(round(salary/12))
if monthly_salary >= 1000:
    max_sacrifice = 1000
else:
    max_sacrifice = monthly_salary - 100
initial_debt = debt = st.slider("What's your remaining student debt?", 1000, 100000)
grad_year = st.slider("Which year did you graduate?", 1998, 2021)
option = st.selectbox(
    'What type of student loan do you have?',
    ('Type 1 (I started uni before 2012)',
     'Type 2 (I started uni on or after 2012)',
     'SAAS Loan (Plan 4 Scottish)'))

#Advanced settings hidden by default
index = False 
if st.checkbox("Show advanced options:", False): #inorder to keep default as unchecked, so settig the flag to False
    st.subheader("Loan Settings") #else true , it will load_data.
    st.sidebar.markdown("Expected pay rise")
    an_pay_rise = 1 + (st.slider('What is your expected percentage annual pay rise', 0, 10))/100
    st.sidebar.markdown("Investments")
    sacrifice = 12*st.slider('What amount of monthly income would you like to invest',0, max_sacrifice)
    invest_type = st.selectbox(
    'How would you like to invest this income sacrifice?',
    ('Student loan overpayments',
     'Index funds'))
    
    if invest_type == 'Student loan overpayments': # The "effect" of the investment type option 
        overpayments = sacrifice
        stock = 0 
    else:
        overpayments = 0
        stock = sacrifice
        index = True 
else: #If the user decides to ignore the advanced settings then all "extra" varibales are by default set to 0 
    an_pay_rise = 1
    sacrifice = 0
    stock = 0
    overpayments = 0 

###-Data --------------------------------------------------------------------------------------------------------
#Tax Brackets 
personal_allowance = 12570 # This is the first tax bracket 
tax_bracket_2 = 50270
reduced_allowance = 100000
no_allowance = 125000
tax_bracket_3 = 150000
# Tax Rates 
tax_rate_1 = 0
tax_rate_2 = 0.2
tax_rate_3 = 0.4
tax_rate_4 = 0.45
#National Insurance brackets 
NI_bracket_1 = 9568
NI_bracket_2 = 50270
#National insurance rates 
NI_rate_1 = 0
NI_rate_2 = 0.12
NI_rate_3 = 0.02
#Student debt key figures 
threshold = 27288
threshold_plan1 = 19390
threshold_plan4 = 25000
debt_rate_1 = 0
debt_rate_2 = 0.09
reduced_personal_allowance = (personal_allowance - (salary - reduced_allowance)/2)
#Student debt brackets 
interest_bracket_1 = 27295 
interest_bracket_2 = 49130
#Student debt interest rates and years until voided 
interest_rate_1 = 0.015
interest_rate_2 = 0.015
interest_rate_3 = 0.045
interest_rate_planalt = 0.011
#Miscellaneous
current_year = 2021
#Not sure where to put this for now 
if option == "Type 2 (I started uni on or after 2012)":
    void_year = void_year = 30 - (current_year - grad_year)
else:
    void_year = 25 - (current_year - grad_year)
###-Functions -----------------------------------------------------------------------------------------------------------------------
##Function to find takehome income       
def monthly_income():
    #Globals
    #
    global tax 
    global NI
    global repay 
    global income
    
    #Tax
   #
    if salary <= personal_allowance:
        tax = tax_rate_1
    elif salary <= tax_bracket_2: 
        tax = (salary - personal_allowance) * tax_rate_2  
    
    elif salary <= no_allowance:
        tax = (salary - tax_bracket_2) * tax_rate_3 + (tax_bracket_2 - reduced_personal_allowance)* tax_rate_2 

    elif salary <= tax_bracket_3: 
        tax = (salary - tax_bracket_2) * tax_rate_3 + (tax_bracket_2) * tax_rate_2   
    else:
        tax = (salary - tax_bracket_3) * tax_rate_4 + (tax_bracket_3 - tax_bracket_2) * tax_rate_3 + (tax_bracket_2) * tax_rate_2
   
    #National Insurance
    #
    if salary <= NI_bracket_1:
        NI = NI_rate_1
    elif salary <= NI_bracket_2: 
        NI = (salary - NI_bracket_1) * NI_rate_2  
    else:
        NI = (salary - NI_bracket_2) * NI_rate_3 + (NI_bracket_2 - NI_bracket_1) * NI_rate_2
        
    #Student debt repayments
    #
    if option == "Type 1 (I started uni before 2012)":
        if salary <= threshold_plan1:
            repay = salary*debt_rate_1
        else:
            repay = (salary-threshold_plan1)*debt_rate_2
    elif option == "Type 2 (I started uni on or after 2012)":
        if salary <= threshold:
            repay = salary*debt_rate_1
        else:
            repay = (salary-threshold)*debt_rate_2          
    else:
        if salary <= threshold_plan4:
            repay = salary*debt_rate_1
        else:
            repay = (salary-threshold_plan4)*debt_rate_2
        
    #Earn x and you'll take home y
    #
    income = (salary - tax - NI - repay)
    monthly = round(income/12)
    st.write(f"""
             From your salary of £{salary} in 2021/2022 you'll take home £{round(income)}.
             This means £{monthly} in your pocket a month.
             """)
    

##Function to find how soon student debt will be payed back with minimum repayments   
#Self generating lists to form data fram -> lineplot and tables.
#
count = 0
debt_payed = 0
accu_int = 0
overpayments_total = 0
years = []
salary_list = []
debt_list = []
int_rate_list = []
debt_payed_list = []
int_year_list = []
#total_payed_list = [] #Not implimented yet 
#total_int_list =[]    #
def time_to_repay(option, debt, salary):
    #Globals
    #
    global count
    global debt_payed
    global accu_int
    global overpayments_total
    global years
    global salary_list
    global debt_list
    global debt_payed_list 
    global void_year 
    #global total_payed_list
    #global total_int_list
    while debt > 0:
        debt_list.append(round(debt)) #Appends in the time to pay function are messy but have to be in the places they are. 
        salary_list.append(round(salary))
        
        #Debt interest rate calculation
        #
        if option == "Type 1 (I started uni before 2012)":
            IR = interest_rate_planalt
        
        elif option == "Type 2 (I started uni on or after 2012)":
            if salary <= interest_bracket_1:
                IR = interest_rate_1
            elif salary <= interest_bracket_2: 
                IR = (((salary - interest_bracket_1) / (interest_bracket_2 - interest_bracket_1)) * (interest_rate_3 - interest_rate_2)) + interest_rate_2    
            else:
                IR = interest_rate_3
        else:
            IR = interest_rate_planalt
        IR = round(IR,4)
        int_rate_list.append(IR)
        
        #Check to see if salary is over the threshold for repaments
        #
        if salary <= threshold:
            rate_repay = debt_rate_1
        else:
            rate_repay = debt_rate_2
            
        #Collection of variables that change over the year
        #
        accu_int += IR*debt
        int_year_list.append(round(IR*debt))
        debt_payed_list.append(round(rate_repay*(salary - threshold) + overpayments))
        debt += IR*debt - rate_repay*(salary - threshold) - overpayments
        salary = salary*an_pay_rise
        overpayments_total += overpayments
        debt_voided = False
        
        #Check to see if it will take greater than 30 years to pay off debt
        #
        if count >= void_year:
            st.write(f"""
                     Your current loan interest rate is {int_rate_list[1]}, but this will increase as
                     you earn more. Your interest rate is calculated based on the country you lived
                     in when you took out your loan, the year you started university, and your current
                     salary.
                     """)
                     
            st.write(f"""
                     Based on the information provided your remaining loan will be forgiven 30 years
                     after graduation - in {years[-1]+1}. The remaining years until this date have been used in the
                     calculations. At your current salary you are not set to pay off your student loan
                     from salary deductions. You will pay back £{sum(debt_payed_list)} before your loan
                     is forgiven.However, at the end of the repayment period your outstanding balance
                     of £{round(debt)} will be written off, meaning you will never have to pay this back.
                     """)
                     
            years.append(current_year + count +1) #Since all arrays must be of the same length
            debt_voided = True
            break
        else:
            years.append(current_year + count)
            count +=1
            
    #applies if and only if debt is reduced to 0 before count reaches 30
    #
    if not debt_voided:
        debt_payed = accu_int + initial_debt + overpayments
        st.write(f"""
                 Your current loan interest rate is {int_rate_list[0]}, but this will increase as you
                 earn more. Your interest rate is calculated based on the country you lived in when you
                 took out your loan, the year you started university, and your current salary.
                 """)
                 
        if overpayments != 0:
            st.write(f"""
                     You will manage to pay off your student loan {count} years from now through a combination of salary deductions and overpayments.
                     You will pay back £{round(debt_payed)} in total, meaning you will pay £{round(accu_int)}
                     in interest (or {round(100*accu_int/initial_debt, 1)}% of the current loan balance).
                     """)
        else:
            st.write(f"""
                     You will manage to pay off your student loan {count} years from now through salary deductions alone.
                     You will pay back £{round(debt_payed)} in total, meaning you will pay £{round(accu_int)}
                     in interest (or {round(100*accu_int/initial_debt, 1)}% of the current loan balance).
                     """)
    if salary >= threshold:
        debt_payed_list.pop()
        debt_payed_list.append(debt_list[-1] + int_year_list[-1])


##Function for index funds
yearly_pay_in = sacrifice
yearly_pay_in_2 = sacrifice  # Total investment + it's gain. Currently -> Initial investment
r = 8                 # Rate of growth 
years_elapsed = 1     # Length in years of elapsed time per iteration 
year_counter = 0 
year_start_compound = current_year 
year_list_2 = []
year_list_3 = []
accumulated_amount_list = []
accumulated_amount_option2_list = []  # Amount accumlated over each years 
def compound_interest(yearly_pay_in,r,years_elapsed,year_start):
    #Globals
    #
    global year_counter
    global yearly_pay_in_2
    while year_counter < 30:
        year_list_2.append(year_start_compound + year_counter)
        if year_list_2[-1] < years[-1]:
            accumulated_amount_option2_list.append(0)
            yearly_pay_in_2 = 0
        else:
            accumulated_amount_option2_list.append(round(yearly_pay_in_2*((1+r/100)*years_elapsed)))
        #
        accumulated_amount_list.append(round(yearly_pay_in*((1+r/100)*years_elapsed)))
        yearly_pay_in += (round(yearly_pay_in*((1+r/100)*years_elapsed)) + sacrifice) - yearly_pay_in
        yearly_pay_in_2 += (round(yearly_pay_in_2*((1+r/100)*years_elapsed)) + sacrifice) - yearly_pay_in_2
        year_counter +=1

###-"The Verdict" ----------------------------------------------------------------------------------------------
st.subheader("The Verdict")
st.sidebar.subheader("The Verdict")
monthly_income()                    # Application of functions
time_to_repay(option, debt, salary) # "                      "

##Data Frame
#
df = pd.DataFrame(
    {
     'Year': [f"{y}" for y in years],
     'salary': [f"£{s}" for s in salary_list],
     'Debt': [f"£{d}" for d in debt_list],
     'Int. Rate %': [f"{i}" for i in int_rate_list],
     'Payed This Year': [f"{p}" for p in debt_payed_list],
     'Interest This Year': [f"{t}" for t in int_year_list]
     #'Total Payed': [f"{tp}" for tp in total_payed_list],
     #'Total Interest': [f"{ti}" for ti in total_int_list]
     },
     columns=['Year', 'salary', 'Debt', 'Int. Rate %', 'Payed This Year', 'Interest This Year' ]
)

##Linegraph
#Table for Linegraph
y_data_max = df.max()
y_data_min = df.min()
df2 = pd.DataFrame(
    {
     'Year': [f"{y}" for y in years],
     'Debt': [f"{d}" for d in debt_list],
     'Payed This Year': [f"{p}" for p in debt_payed_list],
     },
     columns=['Year', 'Debt', 'Payed This Year']
)
    
df2 = df2.melt('Year', var_name=['name',], value_name='value')

#Graph
chart = alt.Chart(df2).mark_line().encode(
x=alt.X('Year:N'),
y=alt.Y('value:Q'),
color=alt.Color("name:N")
).properties(title="")


##Pie chart breakdown of debt repayment, where the slices will be ordered and plotted counter-clockwise:
#
debt_payed = accu_int + initial_debt
labels = 'Initial Debt', 'Total Interest'
sizes = [initial_debt/debt_payed, accu_int/debt_payed]
explode = (0, 0) # none explode 

fig2, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

##Layout
st.table(df)
col1, col2 = st.columns(2)
with col1:
    st.altair_chart(chart, use_container_width=True)
with col2:st.pyplot(fig2)


###-"Additional Plots" -----------------------------------------------------------------------------------------
st.subheader("Salary Breakdown with info")
st.sidebar.subheader("Additional Plots and investment advice")
##Pie chart breakdown of salary, where the slices will be ordered and plotted counter-clockwise: 
#
labels = 'Income Tax', 'National Insurance', 'Student loan repayments', 'Overpayments', 'Takehome pay'
sizes = [tax/salary, NI/salary, repay/salary, (overpayments)/salary, (income-(overpayments))/salary ]
explode = (0, 0, 0, 0, 0.01)  # only "explode" the 4th slice (i.e. 'Takehome pay')

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.   

col1, col2 = st.columns(2) # Need to find a better way of formatting this 
with col1:
    txt = st.write(f'''
                      Since your salary is £{round(salary)} you will pay: £{round(tax)} in tax, £{round(NI)} in national insurance,
                      and £{round(repay)} in student loan repayments per annum. In addition you have decided to invest an additional
                      £{round(sacrifice)} each year.
                      
                      The final value being the exeption the above payments are decided baised on salary with respect
                      to the brackets of payment provided by the Goverment.
                       ''')
    #image = Image.open('Tax.PNG')
    #link_3 = "[Rates and bands for England and wales](https://www.gov.uk/repaying-your-student-loan/what-you-pay) "
   # st.image(image, caption=link_3)   
with col2:st.pyplot(fig1)

###-"Index Funds"-------------------------------------------------------------------------------------------------
compound_interest(yearly_pay_in,r,years_elapsed,year_start_compound)
# Data frame for index fund graph
#
df3 = pd.DataFrame(
    {
     'Year': [f"{y}" for y in year_list_2],
     'Early Investment': [f"{a}" for a in accumulated_amount_list],
     'Investment After Debt repayed':[f"{b}" for b in accumulated_amount_option2_list],
     },
    columns=['Year', 'Early Investment', 'Investment After Debt repayed']
)

df3 = df3.melt('Year', var_name=['name',], value_name='value')

#Linegraph for index fund 
#
chart = alt.Chart(df3).mark_line().encode(
x=alt.X('Year:N'),
y=alt.Y('value:Q'),
color=alt.Color("name:N")
).properties(title="Index fund")
col1, col2 = st.columns(2)

st.altair_chart(chart, use_container_width=True)

if not index: # The "effect" of the investment type option 
    txt = st.write(f'''
                   You chose to invest your monthly sacrifice of £{sacrifice} into Student Debt overpayments. This has
                   accumulated into a final amount of £{accumulated_amount_option2_list[-1]}. However, you would have accumulated
                   an amount equal to £{accumulated_amount_list[-1]}.
                   ''')
else:
    txt = st.write(f'''
                   You chose to invest your monthly sacrifice of £{sacrifice} into Index Funds. This has
                   accumulated into a final amount of £{accumulated_amount_option2_list[-1]}. However, 
                   you have spent an additional £ in interest while paying back your loan.
                   ''')

