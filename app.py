import json, requests
from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
from keys import *
app = Flask(__name__)


client = MongoClient(mongodb) # MongoDB access.

webhook = hook # Discord webhook for reporting

Settings = {
    'domain':'https://crying.world',
    
}

@app.route('/', methods=['GET'])
def hello_world():
    return '''<h1>NoBot Backend.</h1>
           '''


@app.errorhandler(500)
def server_error(e):
    return redirect(f'{Settings["domain"]}/error')

@app.errorhandler(404)
def endpoint_notfound(e):
    return '<h1>Endpoint not found</h1>', 404



@app.route('/verify', methods=['POST'])
def verify():
    token = request.args.get('token')
    requestdata = str(request.form.get('g-recaptcha-response'))
    check = requests.post('https://www.google.com/recaptcha/api/siteverify',{
        'secret':'',
        'response':requestdata,
    })
    json_response = json.loads(check.text)
    
    if json_response['success'] == 'False':
        return 'Invalid reCaptcha response.'
    else:
        db = client['bot']
        
        collection = db['tokens']
        
        user_collection = db['all_users']
        
        update = collection.update_one({'token':str(token)}, {'$set':{'verified':'True'}})
        
        find = collection.find({'token':str(token)})
        
        for r in find:
            token_id = r['token']
            user_name = r['user']
            user_identiy = r['user_id']
            guild_id = r['guild_id']
            guild_name = r['guild']
            verified = r['verified']
        
        user_agent = request.user_agent.string
        
        client_remote_address = request.headers['X-Forwarded-for']
        
        ip = client_remote_address.split(',')[0]
        
        db = client['bot']
        collection = db['all_users']
        payload={
            'user':str(user_name),
            'user_id':str(user_identiy),
            'guild':str(guild_name),
            'guild_id': str(guild_id),
            'user_agent': str(user_agent),
            'IP': str(ip),
        }
        
        collection.insert_one(payload)
            
        return redirect(f'{Settings["domain"]}/success')
    

@app.route('/relay', methods=['POST'])
def bugreport():
    name = str(request.form.get('name'))
    
    type_of = str(request.form.get('type_of'))
    
    issue = str(request.form.get('issue'))
    
    requestdata = str(request.form.get('g-recaptcha-response'))
    
    check = requests.post('https://www.google.com/recaptcha/api/siteverify',{
        'secret':'',
        'response':requestdata,
    })
    
    json_response = json.loads(check.text)
    
    if json_response['success'] == 'False':
        return 'Invalid reCaptcha response.'
    else:
        send = requests.post(webhook, data={
            'content':f'Reporter: `{name}`, `{type_of}`. The issue is: `{issue}` ',
            'avatar_url':'https://cdn2.iconfinder.com/data/icons/glyph-web-application-1/64/bug_development_software_coding_error-512.png' #some random bug
        })
        return redirect(Settings['domain'])


@app.route('/ban-check/<int:user_id>', methods=['GET'])
def checkban(user_id):
    db = client['bot']
    collection = db['global_bans']
    search_ban = collection.find({'user_id': str(user_id)})
    if search_ban.count() > 0:
        for r in search_ban:
            user = r['user_id']
            reason = r['reason']
            data = {
            'user_id':str(user),
            'reason':str(reason),
            }
            return jsonify(data)
    else:
        data = {
        'status':'Not banned',
        }
        return jsonify(data)

@app.route('/check', methods=['GET'])
def check():
    token = request.args.get('token')
    
    db = client['bot']
    collection = db['tokens']
    search_token = collection.find({'token':str(token)})
    
    for r in search_token:
        token_id = r['token']
        user_name = r['user']
        user_identiy = r['user_id']
        guild_id = r['guild_id']
        verified = r['verified']
        if str(verified) == 'True':
            data = {
                'verified':'True'
            }
            return jsonify(data)
        elif str(verified) == 'False':
            data = {
                'verified': 'False'
            }    
            return jsonify(data)
        else:
            data = {
                'response':'an error occured'
            }
            return jsonify(data)
    
    
if __name__ == '__main__':
   app.run()
   
