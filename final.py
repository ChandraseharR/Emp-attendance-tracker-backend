import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict,Union
from datetime import datetime,date,timedelta
import pandas as pd
import numpy as np
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
cur=None
conn=None
app = FastAPI()
    
origins = [
    "http://localhost:3000"
]
                            
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    global conn
    conn = psycopg2.connect(
        database="postgres", # database name
        user = "postgres", # user name
        password = "c#@ndru 12", #password
        host = "localhost", # host
        port = "5432" # port number enabled by you
    )
    global cur
    cur = conn.cursor()
@app.on_event("shutdown")
async def shutdown():
    await conn.commit()
    await conn.close()






table_name1="employee"
class employee(BaseModel):
    emp_id:int = Field(..., example=1001)
    name: str = Field(..., example="Manjot Singh")
    tag_id: int = Field(..., example=200)
    role_id : int = Field(..., example=2)
class UpdateEmployeeData(BaseModel):
    name: str = Field(..., example="Enter Empname")
    tag_id: int = Field(..., example="Enter TagId")
    role_id: int = Field(..., example="Enter Role")
def get_data_as_json(lt):
    ans = []
    for row in lt:
        temp = { 'emp_id' : row[0], 'name': row[1], 'tag_id': row[2], 'role_id': row[3] }
        ans.append(temp)
    return ans

@app.get('/getAllEmployees')
async def all_employees():
    cur.execute(f'SELECT * FROM "{table_name1}"')
    return get_data_as_json(cur.fetchall())

@app.get('/getEmployeeByID', response_model = List[employee])
async def get_employee_by_id(empid: int):
    cur.execute(f'SELECT * FROM "{table_name1}" where "emp_id"={empId}')
    return get_data_as_json(cur.fetchall())

@app.post('/registerEmployee', response_model = List[employee])
async def register_employee(employee : employee):
    cur.execute(f'INSERT INTO "{table_name1}"("emp_id", "name", "tag_id", "role_id") VALUES(%s, %s, %s, %s)', 
    (employee.emp_id, employee.name, employee.tag_id, employee.role_id))

    conn.commit()

    return await get_employee_by_id(employee.empid)
    
@app.put('/updaterEmployeeData', response_model = List[employee])
async def update_employee_data(empid: int, data_changed : Update_Employee_Data):
    cur.execute(f'UPDATE "{table_name1}" SET "name" = %s, "tag_id" = %s, "role_id" = %s WHERE "emp_id" = %s', 
    (data_changed.name, data_changed.tag_id, data_changed.role_id, empid))

    conn.commit()
    return await get_employee_by_id(empid)

@app.delete('/employeeDelete/{empid}')
def delete_employee(empid: int):
    cur.execute(f'DELETE FROM "{table_name1}" WHERE "emp_id" = %s', (empid,))
    conn.commit()
    return "Employee with " + str(empid) + " is deleted"    


table_name2="login_credentials"
class login(BaseModel):
    emp_id:int = Field(..., example=102)
    password:str = Field(..., example='emp102')
def get_data_as_json2(lt):
    temp={}
    for row in lt:
        temp = { 'emp_id' : row[0], 'name': row[1], 'role': row[2] }
    return temp

@app.post('/login')
async def validate_login(login_val:login):
    cur.execute(f'SELECT emp_id,name,role from (SELECT emp_id,name,role_id,password from "{table_name2}" natural join "employee") as X natural join "employee_role" where emp_id={login_val.emp_id} and password=\'{login_val.password}\'')
    res=cur.fetchall()
    data=list(res)
    if len(data)==0:
        return {"message":"Invalid Username/Password"}   
    return get_data_as_json2(res)
    

table_name3="in_out"
class analytics(BaseModel):
    tag_id:int = Field(..., example=201)
    in_time: datetime = Field(..., example="2022-09-03 10:08:34")
    out_time: datetime = Field(..., eexample="2022-09-03 10:08:34")
    id : int = Field(..., example=2)
def get_data_as_json3(lt):
    ans = []
    for row in lt:
        temp = { 'userID' : row[0], 'userName': row[1] }
        ans.append(temp)
    return ans


@app.get('/getAnalyticsByID')
async def get_employee_by_id(empid: int):
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and "id"!=4')
    data1=cur.fetchall()
    wdict={}
    wdict_time={}
    for row in data1:
        print(row)
        if row[0].date()==row[1].date(): 
            if row[0].date() not in wdict:
                wdict[row[0].date()]=datetime(1, 1, 1, 0, 0)
                wdict_time[row[0].date()]=0
                wdict[row[0].date()]+=(row[1]-row[0])
                wdict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
            else:
                wdict[row[0].date()]+=(row[1]-row[0])
                wdict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
    print(wdict_time)
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and "id"=4')
    data1=cur.fetchall()
    ldict={}
    ldict_time={}
    for row in data1:
        if row[0].date()==row[1].date(): 
            if row[0].date() not in ldict:
                ldict[row[0].date()]=datetime(1, 1, 1, 0, 0)
                ldict_time[row[0].date()]=0
                ldict[row[0].date()]+=(row[1]-row[0])
                ldict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
            else:
                ldict[row[0].date()]+=(row[1]-row[0])
                ldict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
    ans = []            
    for i in wdict:
        wdict[i]=wdict[i].time()
        ldict[i]=ldict[i].time()
        print("Date:",i)
        print("Working Hours:",wdict[i])
        print("Leisure Hours:",ldict[i])
        print("\n")
        temp={ 'Date' : i , 'workingHours': wdict_time[i],'leisureHours': ldict_time[i],'Working Hours' : wdict[i] , 'Leisure Hours' : ldict[i] }
        ans.append(temp)
    return ans
    
@app.get('/getLatestAnalyticsByID')
async def get_employee_by_id(empid: int):
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and "id"!=4')
    data1=cur.fetchall()
    wdict={}
    wdict_time={}
    for row in data1:
        print(row)
        if row[0].date()==row[1].date(): 
            if row[0].date() not in wdict:
                wdict[row[0].date()]=datetime(1, 1, 1, 0, 0)
                wdict_time[row[0].date()]=0
                wdict[row[0].date()]+=(row[1]-row[0])
                wdict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
            else:
                wdict[row[0].date()]+=(row[1]-row[0])
                wdict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
    print(wdict_time)
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and "id"=4')
    data1=cur.fetchall()
    ldict={}
    ldict_time={}
    for row in data1:
        if row[0].date()==row[1].date(): 
            if row[0].date() not in ldict:
                ldict[row[0].date()]=datetime(1, 1, 1, 0, 0)
                ldict_time[row[0].date()]=0
                ldict[row[0].date()]+=(row[1]-row[0])
                ldict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
            else:
                ldict[row[0].date()]+=(row[1]-row[0])
                ldict_time[row[0].date()]+=(row[1]-row[0]).total_seconds()
    ans = []           
    for i in wdict:
        wdict[i]=wdict[i].time()
        if i in ldict:
            ldict[i]=ldict[i].time()
        else:
            ldict[i]='00:00:00' 
            ldict_time[i]=0   
        print("Date:",i)
        print("Working Hours:",wdict[i])
        print("Leisure Hours:",ldict[i])
        print("\n")
        temp={ 'Date' : i , 'workingHours': wdict_time[i],'leisureHours': ldict_time[i],'Working Hours' : wdict[i] , 'Leisure Hours' : ldict[i] }
        ans.append(temp)

    return ans[-1]   

@app.get('/getAnalyticsByIDandDate')
async def get_employee_by_id(empid: int, date:date):
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{date}\' and "id"!=4')
    data1=cur.fetchall()
    wsum=datetime(1, 1, 1, 0, 0)
    wsum_time = 0
    for row in data1:
        wsum+=(row[1]-row[0])
        wsum_time+=(row[1] - row[0]).total_seconds()

    print(f'wsum = {wsum}')
    print(wsum.time())
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{date}\' and "id"=4')
    data2=cur.fetchall()
    lsum=datetime(1, 1, 1, 0, 0)
    lsum_time = 0
    for row in data2:
        lsum+=(row[1]-row[0])
        lsum_time+=(row[1] - row[0]).total_seconds()

    print(lsum.time())  
    temp = { 'Date' : date , 'workingHours': wsum_time, 'leisureHours': lsum_time, 'Working Hours' : wsum.time() , 'Leisure Hours' : lsum.time()}
    return temp

@app.get('/getAttendaceByID')
async def get_employee_by_id(empid: int,m:int,y:int):
    cur.execute(f'SELECT DISTINCT DATE("in_time") FROM "{table_name3}" natural join "employee" where "emp_id"={empid}')
    data=pd.DataFrame(cur.fetchall(),columns=['date'])
    str2=""
    leap = 0
    if y% 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y% 4 == 0:
        leap = 1
    if m==2:
        s1=28 + leap
        s1=str(s1)
        y=str(y)
        m=str(m)
        str2+=y+"-"+m+"-"+s1
    lst = [1,3,5,7,8,10,12]
    if m in lst:
        y=str(y)
        m=str(m)
        str2+=y+"-"+m+"-"+"31"
    else:
        y=str(y)
        m=str(m)
        str2+= y+"-"+m+"-"+"30"
    str1= y+"-"+m+"-"+"01"      
    data['date'] = pd.to_datetime(data['date'])
    my_range= pd.date_range(start=str(str1), end=str(str2), freq='B')
    absent=len(my_range.difference(data['date']))
    days = len(pd.bdate_range(str(str1),str(str2))) 
    m=str(m)
    datetime_object = datetime.strptime(m, "%m")
    present=days-absent
    full_month_name = datetime_object.strftime("%B")
    temp = { 'Month' : full_month_name , 'Present' : present , 'Absent' : absent}
    return temp

@app.get('/getYearlyAttendaceByID')
async def get_employee_by_id(empid: int,y:int):
    cur.execute(f'SELECT DISTINCT DATE("in_time") FROM "{table_name3}" natural join "employee" where "emp_id"={empid}')
    data=pd.DataFrame(cur.fetchall(),columns=['date'])
    today = datetime.now()
    ans=[]
    lst = [1,3,5,7,8,10,12]
    leap = 0
    d=0
    if y% 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y% 4 == 0:
        leap = 1
    for m in range(1,today.month+1):    
        if m==2:
            s1=28 + leap
            y=str(y)
            m=str(m)
            s2=str(s1)
            str2=y+"-"+m+"-"+s2
   
        elif m==today.month: 
            y=str(y)
            m=str(m)
            dd=str(today.day)
            str2=y+"-"+m+"-"+dd
  

        elif m in lst:
            y=str(y)
            m=str(m)
            str2=y+"-"+m+"-"+"31"
   
        else:
            y=str(y)
            m=str(m)
            str2= y+"-"+m+"-"+"30"

        str1= y+"-"+m+"-"+"01"      
        data['date'] = pd.to_datetime(data['date'])
        my_range= pd.date_range(start=str(str1), end=str(str2), freq='B')
        absent=len(my_range.difference(data['date']))
        days = len(pd.bdate_range(str(str1),str(str2))) 
        m=str(m)
        datetime_object = datetime.strptime(m, "%m")
        present=days-absent
        full_month_name = datetime_object.strftime("%B")
        temp = { 'Month' : full_month_name , 'Present' : present , 'Absent' : absent}
        ans.append(temp)
    return ans

@app.get('/getWeeklyData')
async def get_weekly_data(empid:int):
    t0=date.today()
    t0=str(t0)
    print(t0)
    dict = {'Date':[t0]}  
    df = pd.DataFrame.from_dict(dict)  
    df['Date'] = pd.to_datetime(df['Date'], errors ='coerce')
    df.astype('int64').dtypes  
    week_number = df['Date'].dt.week
    print(week_number)
    def get_date_range_from_week(p_year,p_week):
        firstdayofweek = datetime.strptime(f'{p_year}-W{int(p_week )- 1}-1', "%Y-W%W-%w").date()
        lastdayofweek = firstdayofweek + timedelta(days=5)
        return firstdayofweek, lastdayofweek
    firstdate, lastdate =  get_date_range_from_week('2022',week_number)
    st=firstdate
    delta=timedelta(days=1)
    ans=[]
    for i in range(1,6):
        print(st)
        cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{st}\' and "id"!=4')
        data1=cur.fetchall()
        wsum=datetime(1, 1, 1, 0, 0)
        wsum_time = 0
        for row in data1:
            wsum+=(row[1]-row[0])
            wsum_time+=(row[1] - row[0]).total_seconds()
        print(f'wsum = {wsum}')
        print(wsum.time())
        cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{st}\' and "id"=4')
        data2=cur.fetchall()
        lsum=datetime(1, 1, 1, 0, 0)
        lsum_time = 0
        for row in data2:
            lsum+=(row[1]-row[0])
            lsum_time+=(row[1] - row[0]).total_seconds()
        print(lsum.time())  
        print(st.strftime("%A"))
        temp = { 'Date' : st ,'Day': st.strftime("%A") ,'workingHours': wsum_time, 'leisureHours': lsum_time, 'Working Hours' : wsum.time() , 'Leisure Hours' : lsum.time()}
        ans.append(temp)
        st+=delta
    return ans 


@app.get('/getAnalyticsByFloor')
async def get_employee_by_id(empid: int,date:date):
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{date}\'')
    data1=cur.fetchall()
    whrs=datetime(1, 1, 1, 0, 0)
    temp=[]
    count=int(1)
    for row in data1:
        whrs=datetime(1, 1, 1, 0, 0)
        intime=row[0].time()
        outtime=row[1].time()       
        whrs+=row[1]-row[0]
        ans={ 'Sno':count,'Floor':row[2],'InTime' : intime , 'OutTime' : outtime , 'duration' : whrs.time()}#,duration_sec' : wsum}
        temp.append(ans) 
        count+=1
    return temp
@app.get('/getAllAnalyticsByFloor')
async def get_employee_by_id(empid: int,date:date, floor: Union[int, None]=None):
    if floor:
         cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{date}\' and "id"={floor}')
    else:
         cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{date}\'')
    data1=cur.fetchall()
    ans=[]
    for row in data1:
        whrs=datetime(1, 1, 1, 0, 0)
        intime=row[0].time()
        outtime=row[1].time()       
        whrs+=row[1]-row[0]
        print(whrs.time().hours())
        print(whrs.time().minutes())
        print(whrs.time().seconds())
        if floor:
            temp = { 'Floor':floor,'InTime' : intime , 'OutTime' : outtime , 'duration' : whrs.time()}#,duration_sec' : wsum}
        else:
             temp = { 'Floor':row[3],'InTime' : intime , 'OutTime' : outtime , 'duration' : whrs.time()}#,duration_sec' : wsum}
        ans.append(temp)    
    return ans
      
@app.get('/getAnalyticsByID2')
async def get_employee_by_id(empid: int):
    test_date=date.today()
    diff = 1
    if test_date.weekday() == 0:
        diff = 3
    elif test_date.weekday() == 6:
        diff = 2
    else :
        diff = 1
    tdate = test_date - timedelta(days=diff)
    print(tdate)
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={empid} and DATE("in_time")=\'{tdate}\' and "id"!=4')
    data1=cur.fetchall()
    wsum=datetime(1, 1, 1, 0, 0)
    wsum_time = 0
    for row in data1:
        wsum+=(row[1]-row[0])
        wsum_time+=(row[1] - row[0]).total_seconds()

    print(f'wsum = {wsum}')
    print(wsum.time())
    cur.execute(f'SELECT "in_time","out_time","id","emp_id" FROM "{table_name3}" natural join "employee" where "emp_id"={EmpId} and DATE("in_time")=\'{tdate}\' and "id"=4')
    data2=cur.fetchall()
    lsum=datetime(1, 1, 1, 0, 0)
    lsum_time = 0
    for row in data2:
        lsum+=(row[1]-row[0])
        lsum_time+=(row[1] - row[0]).total_seconds()
    print(lsum.time())  
    temp = { 'Date' : tdate , 'workingHours': wsum_time, 'leisureHours': lsum_time, 'Working Hours' : wsum.time() , 'Leisure Hours' : lsum.time()}
    return temp
            
