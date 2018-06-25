from flask import Flask, request, render_template, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from warrant import Cognito
from flask import jsonify
from boto3.dynamodb.conditions import Key, Attr
import boto3
import uuid
import os
import json



app = Flask(__name__,static_folder='static')
def cognitoConfig(argUsername = ""):
    # poolID = os.environ['poolID']
    # cognitoAppClientID = os.environ['cognitoAppClientID']
    if argUsername : 
        # config = Cognito(poolID,cognitoAppClientID, username : aqrUsername )
        config = Cognito("us-east-1_PqI7vgPYC","70uonffglttpu0juiu5p8spom0", username = argUsername )
    else : 
        # config = Cognito(poolID,cognitoAppClientID)
        config = Cognito("us-east-1_PqI7vgPYC","70uonffglttpu0juiu5p8spom0")

    return config

@app.route('/')
def index():
    cognitoConnection = cognitoConfig() 
    userData = cognitoConnection.get_users()
    # for item in userData:
    #     data = item._data
    #     data2 = item.__dict__
        # print(item._data.get('custom:group_name'))

    # group_data = {'GroupName': 'Company', 'Description': 'Company','Precedence': None}
    # group = cognitoConnection.get_group(group_name='Company')
    # print(group.__dict__)

    return render_template("/main/home.html", result = userData)

@app.route('/login')
def login():
    return render_template("/auth/login.html")

@app.route('/register')
def register():
    return render_template("/auth/register.html")

@app.route('/submitLogin', methods = ['POST'])
def submitLogin():
    if request.method == 'POST':
        data = request.form
        userName = data.get('username')
        # password = generate_password_hash(data.get('password'))
        password = data.get('password')
        u = cognitoConfig(userName)
        resp = u.authenticate(password = password)
        # resp = u.admin_authenticate(password = password)

        cognitoConnection = cognitoConfig()
        listUsers = cognitoConnection.get_users()
        return render_template("/main/home.html", result = listUsers)

@app.route('/submitRegister',methods=['POST'])
def submitRegister():   
    if request.method == 'POST':
        # ------------*** Test store data to DynamoDB ***------------------
        # data = request.form
        # form = "register"
        # USERS_TABLE = os.environ['tbUser']
        # client = boto3.client('dynamodb')
        # userId = uuid.uuid4().hex
        
        # client.put_item(
        #     TableName=USERS_TABLE,
        #     Item = {
        #         'userId': {'S': userId }, 
        #         'name': {'S': data.get('name') },
        #         'email': {'S': data.get('email') }, 
        #         'password': {'S': data.get('password') },
        #         'phone': {'S': data.get('phone') }, 
        #         'address': {'S': data.get('address') }
        #     })

        # resp = client.get_item(
        #         TableName=USERS_TABLE,
        #         Key = {'userId': { 'S': userId }}
        #     )


        #Cognito with Warrant : https://github.com/capless/warrant 
        data = request.form
        userName = data.get('name')
        email = data.get('email')
        # password = generate_password_hash(data.get('password'))
        password = data.get('password')
        phone = '+' + data.get('phone')
        address = data.get('address')
        u = cognitoConfig()
        u.add_base_attributes( phone_number = phone, email = email, name = userName, address = address)
        u.add_custom_attributes(group_name = 'Company')
        u.register(userName, password)
        form = "register"
        return render_template("/auth/confirm_register.html", name = userName, form = form)

@app.route("/verifyRegister", methods=['POST', 'GET'])
def verifyRegister():
    if request.method == 'POST':
        data = request.form
        verifyCode = data.get('code')
        userName = data.get('username')
        u = cognitoConfig()
        u.confirm_sign_up(verifyCode, username = userName)
        cognitoConnection = cognitoConfig()
        listUsers = cognitoConnection.get_users()
        return render_template("/main/home.html", result = listUsers)
    else :
        return render_template("/auth/confirm_register.html")

@app.route('/view_user/<name>')
def viewUser(name = ""):
    return render_template("/auth/view_user.html", name = name)


@app.route('/listStoreCompany/<string:companyName>')
def listStoreCompany(companyName = ""):
    return render_template("/store/store_list.html")

@app.route('/addProduct', methods=['POST'])
def addProduct():
    if request.method == 'POST':
        data = request.form
        PRODUCTS_TABLE = "tbProducts"
        client = boto3.client('dynamodb')
        productID = uuid.uuid4().hex
        
        client.put_item(
            TableName = PRODUCTS_TABLE,
            Item = {
                'ID': {'S': productID }, 
                'Name': {'S': data.get('productName') },
                'JAN': {'S': data.get('JAN') }, 
                'LOT': {'S': data.get('LOT') },
                'Company': {'S': data.get('companyName') }, 
            })
        return redirect(url_for('addProductForm', companyName = data.get('companyName')))

@app.route('/addProductForm/<string:companyName>')
def addProductForm(companyName = ""):
    return render_template("/product/add_product.html", companyName = companyName)
        
@app.route('/listProduct/<companyName>')
def listProduct(companyName = ""):
    # PRODUCTS_TABLE = "tbProducts"
    # client = boto3.client('dynamodb')
    # resp = client.query(
    #             TableName = PRODUCTS_TABLE,
    #             KeyConditionExpression=Key('Company').eq(companyName)
    #         )
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('tbProducts')
    response = table.scan(
        FilterExpression=Key('Company').eq(companyName)
    )
    return render_template("/product/product_list.html", companyName = companyName , result = response['Items'])

if __name__ == '__main__':
    app.run(debug = True)