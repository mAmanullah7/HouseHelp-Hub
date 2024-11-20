from dotenv import load_dotenv
# from dotenv import dotenv_value
import os
from app import app

load_dotenv()

curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(curr_dir)   
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['UPLOAD_EXTENSIONS']=['.pdf']
app.config['UPLOAD_PATH']=os.path.join(curr_dir,'static',"pdfs")
