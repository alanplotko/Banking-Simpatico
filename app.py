# Flask
from flask import Flask, render_template, request, redirect, url_for, session, abort, make_response

# Miscellaneous
import os, logging, json, sys, urllib, requests, collections

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Instantiate Authomatic Object and set up app
app = Flask(__name__)
app.config.from_object(__name__)

app.key = "370bb2465e12ee6843ec1b41db2e91cd" # Capital One Key
app.secret_key = "\xfe\xb61\xce~g \xb57h\x15\r\xacXo\xa5\x18\\\xb5\xd4SRk\x87" # App Secret Key

@app.route('/')
def index():
    url = "http://api.reimaginebanking.com/{}?key={}".format("customers", app.key)
    data = json.loads(requests.get(url).text)[1]
    session['manager'] = data
    acccount_url = "http://api.reimaginebanking.com/{}/{}/accounts?key={}".format("customers", session['manager']['_id'], app.key)
    customer_dict = collections.OrderedDict()
    customer_data = json.loads(requests.get(acccount_url).text)
    shadesOfBlue = ["#86BBD8", "#356D9C", "#0C4D8B"]
    count = 0
    print(customer_data)
    for customer in customer_data:
        if customer['type'] == "Checking":
            customer['color'] = shadesOfBlue[count]
            count += 1
        else:
            customer['color'] = "#A12830"
    session['customer_data'] = customer_data
    print(customer_data)
    return render_template('index.html', template_folder=tmpl_dir, customers=session['customer_data'], manager=session['manager'])

@app.route('/account/<customer_id>', methods=["GET", "POST"])
def account(customer_id):
    if request.method == "GET":
        url = "http://api.reimaginebanking.com/{}?key={}".format("customers", app.key)
        data = json.loads(requests.get(url).text)[1]
        session['manager'] = data
        
        if 'current_customer' not in session or ('current_customer' in session and session['current_customer'] != customer_id):
            acccount_url = "http://api.reimaginebanking.com/accounts/{}?key={}".format(customer_id, app.key)
            data = json.loads(requests.get(acccount_url).text)
            session['current_customer'] = data    
        purchase_url = "http://api.reimaginebanking.com/accounts/{}/purchases?key={}".format(customer_id, app.key)
        data = json.loads(requests.get(purchase_url).text)
        sumPurchases = 0
        
        for purchase in data:
            purchase['add_info'] = json.loads(requests.get("http://api.reimaginebanking.com/merchants/{}?key={}".format(purchase["merchant_id"], app.key)).text)
            sumPurchases += purchase['amount']
        session['purchases'] = data
        session['purchase_sum'] = sumPurchases

        hotels_url = "http://priceline.com/api/hotelretail/listing/v3/42.0891413093459,-75.9684558838623/20150923/20150930/1/5?offset=0&sort=4&pageSize=4"
        data = json.loads(requests.get(hotels_url).text)
        session['hotels'] = data

        return render_template('account.html', template_folder=tmpl_dir, current_customer=session['current_customer'], 
            customers=session['customer_data'], manager=session['manager'], purchases=session['purchases'], 
            sumPurchases=session['purchase_sum'], hotels=session['hotels'])
    elif request.method == "POST":
        account_url = "http://api.reimaginebanking.com/customers/{}?key={}".format(customer_id, app.key)
        payload = {
            'address': {}
        }
        if request.form.get('street_number', None) != None and request.form.get('street_number', None) != "":
            payload['address']['street_number'] = request.form.get('street_number', None)
        if request.form.get('street_name', None) != None and request.form.get('street_name', None) != "":
            payload['address']['street_name'] = request.form.get('street_name', None)
        if request.form.get('state', None) != None and request.form.get('state', None) != "":
            payload['address']['state'] = request.form.get('state', None)
        if request.form.get('city', None) != None and request.form.get('city', None) != "":
            payload['address']['city'] = request.form.get('city', None)
        if request.form.get('zip', None) != None and request.form.get('zip', None) != "":
            payload['address']['zip'] = request.form.get('zip', None)
        print(json.dumps(payload))
        req = requests.put(account_url, data=json.dumps(payload), headers={'content-type':'application/json'})
        if req.status_code == 200 or req.status_code == 202:
            message = "Successfully updated profile!"
            url = "http://api.reimaginebanking.com/{}?key={}".format("customers", app.key)
            data = json.loads(requests.get(url).text)[1]
            session['manager'] = data
        else:
            data = json.loads(req.text)
            if data['message'] != None:
                message = "Error code ({}): {} Check the following fields: {}".format(data['code'], data['message'], ", ".join(data['culprit']))
            else:
                message = "Error code ({}): Request failed. Please try again.".format(data['code'])
        return render_template('account.html', template_folder=tmpl_dir, current_customer=session['current_customer'], 
            customers=session['customer_data'], manager=session['manager'], purchases=session['purchases'], 
            sumPurchases=session['purchase_sum'], message=message, hotels=session['hotels'])
    else:
        message = "Error: Method not allowed."
        return render_template('account.html', template_folder=tmpl_dir, current_customer=session['current_customer'], 
            customers=session['customer_data'], manager=session['manager'], purchases=session['purchases'], 
            sumPurchases=session['purchase_sum'], message=message, hotels=session['hotels'])

'''
@app.route('/update/<customer_id>', methods=["POST"])
def account_update(customer_id):
    if request.method == 'POST':
        account_url = "http://api.reimaginebanking.com/customers/{}?key={}".format(customer_id, app.key)
        payload = {
            'address': {}
        }
        if request.form.get('street_number', None) != None and request.form.get('street_number', None) != "":
            payload['address']['street_number'] = request.form.get('street_number', None)
        if request.form.get('street_name', None) != None and request.form.get('street_name', None) != "":
            payload['address']['street_name'] = request.form.get('street_name', None)
        if request.form.get('state', None) != None and request.form.get('state', None) != "":
            payload['address']['state'] = request.form.get('state', None)
        if request.form.get('city', None) != None and request.form.get('city', None) != "":
            payload['address']['city'] = request.form.get('city', None)
        if request.form.get('zip', None) != None and request.form.get('zip', None) != "":
            payload['address']['zip'] = request.form.get('zip', None)
        print(json.dumps(payload))
        req = requests.put(account_url, data=json.dumps(payload), headers={'content-type':'application/json'})
        if req.status_code == 200 or req.status_code == 202:
            message = "Successfully updated profile!"
            url = "http://api.reimaginebanking.com/{}?key={}".format("customers", app.key)
            data = json.loads(requests.get(url).text)[1]
            session['manager'] = data
        else:
            if hasattr(req, 'message'):
                message = "Error code ({}): {} Please try again.".format(req.status_code, req.message)
            else:
                message = "Error code ({}): Request failed. Please try again.".format(req.status_code)
    else:
        message = "Error: Method not allowed."
    print(message)
    return redirect(url_for(accountMessage, customer_id=customer_id, message=message))
'''

@app.errorhandler(401)
def unauthorized(error):
    return render_template('error.html', template_folder=tmpl_dir, error=401, error_msg="Unauthorized",
        return_home="You must be logged in to access this page!"
    )

@app.errorhandler(500)
def internal_server(e):
    return render_template('error.html', template_folder=tmpl_dir, error=500, error_msg="Internal Server Error",
        return_home="Nessie is on break. Try again in a few minutes."
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', template_folder=tmpl_dir, error=404, error_msg="Page Not Found",
        return_home="We can't find what you're looking for. Try again!"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug=True)    