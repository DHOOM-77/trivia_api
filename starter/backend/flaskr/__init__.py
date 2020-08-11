import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions (request,selection):
  page = request.args.get('page',1,type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  
  return current_questions
  

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  
  CORS(app)
  
  
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers","Content-Type-Authorization")
    response.headers.add("Access-Control-Allow-Headers","GET,POST,PATCH,DELET,OPTIONS")
    return response
  
  @app.route('/categories',methods=['GET'])
  def retrieve_category ():
    categories = Category.query.order_by(Category.id).all()
    

    if len(categories)==0:
      abort(404)
    
     
    return jsonify({
      "success" : True,
      "categories": {category.id: category.type for category in categories},
      "total_category" :len(Category.query.all())
    })
  

  
  @app.route('/questions',methods=['GET'])
  def retrieve_question ():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request,selection)
    
    categories = Category.query.order_by(Category.id).all()
    
    if len(current_questions) == 0 :
      abort(404)
      
     
    return jsonify ({
     "success" : True,
     "questions" : current_questions,
     "total_question" :len(Question.query.all()),
     "categories": {category.id: category.type for category in categories},
     "current_category": None 
    })

  
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id): 
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None :
        abort(404)
      
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request,selection)
    
   
      return jsonify({
        "success" : True,
        "deleted" :question_id
      })
    except:
      abort(422)
  

  
  @app.route('/questions',methods = ['POST'])
  def create_question():
    
    body = request.get_json()


    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')
    
    if ((new_question == '') or (new_answer == '') or (new_difficulty == '') or (new_category == '')):
      abort(405)

    try:
      question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty, category=new_category)
      question.insert()

      return jsonify({
        'success': True,
        'created': question.id,
      })

    except:
     abort(422)

  
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    
    
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    if search_term == '' or search_term ==' ':
      abort(404)
      
    
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
    
    if len(questions) == 0:
      abort(404)
      
    return jsonify({
      'success': True,
      'questions': [question.format() for question in questions],
      'total_questions': len(questions),
      'current_category': None
    })
   

  
  @app.route('/categories/<int:category_id>/questions',methods = ['GET'])
  def get_questions_by_categories(category_id):
    try:
      ctegory_type= str(category_id)
              
      questions = Question.query.filter(Question.category==ctegory_type).all()
      
      return jsonify({
          "success" : True,
          "questions" : [question.format() for question in questions],
          "total_questions" :len(Question.query.all()),
         'current_category': category_id
        })
    except: abort(404)


  
  @app.route('/quizzes',methods =['POST'])
  def play_quiz():
    try:

      body = request.get_json()

      category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if category['id'] != 0:
        get_category = Category.query.filter_by(id=category['id']).one_or_none()
        if not get_category:
          abort(404)
        #get questions by specific category
        questions = Question.query.filter_by(category=get_category.id)
      else:
        #get all category
        questions = Question.query.all()
      none_doublicate_question = []
      for question in questions:
          #set the flag
          found = False
          for prev in previous_questions:
            if prev == question.id:
              found = True
              break
          if not found:
           none_doublicate_question.append(question)
      random_index = random.randint(0, len(none_doublicate_question)-1)
      return jsonify({
        'success': True,
        'question': none_doublicate_question[random_index].format()
        })
    except:
        abort(422)

  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
     "success" : False,
     "error" : 404,
      "message" :"resource not found"  
    }),404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({
     "success" : False,
     "error" : 422,
      "message" :"unprossable"  
    }),422
    
  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
     "success" : False,
     "error" : 405,
      "message" :"method not allowed"  
    }),405
  
  return app

    