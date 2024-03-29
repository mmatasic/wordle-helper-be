from flask import Flask, json, request, jsonify, make_response
from wordle_helper import getApiResult
from model import HelperResponse

api = Flask(__name__)
api.config['JSON_AS_ASCII'] = False
@api.route('/wordle', methods=['GET'])
def getPossible():
  lang = request.args.get('lang')
  if not lang:
    lang = 'hr'
  globs = request.args.get('globs')
  if not globs:
    globs=''
  globs = globs.replace(' ', '+')
  result = getApiResult(lang, globs)
  response =json.dumps(vars(result))
  print(response)
  response = make_response(jsonify(response))
  response.headers.add("Access-Control-Allow-Origin", "*")
  return response

if __name__ == '__main__':
  api.run(host='0.0.0.0') 
