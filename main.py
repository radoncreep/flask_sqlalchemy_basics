from flask import Flask, views
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# model schema
class VideoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # nullable meaning name is required
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    # prints the object representation of what the db looks like internally
    def __repr__(self):
        return f"Video(name={self.name}, views={self.views}, likes={self.likes})"

# db.create_all() once exexuted once delete this once createed to avoid overwritting db

names = {
    "victor": {
        "age": 22,
        "gender": "male"
    },
    "tim": {
        "age": 20,
        "gender": "male"
    }
}

# makes sure information parsed follows the expectedd structure
# request parser
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("likes", type=int, help="Likes of video is required", required=True)
video_put_args.add_argument("views", type=int, help="Views of videois required", required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str)
video_update_args.add_argument("likes", type=int)
video_update_args.add_argument("views", type=int)



# error handling

# def abort_if_video_id_nonexistent(video_id):
#     """
#         cancels request if the video id requested does not exist
#     """
#     if video_id not in videos:
#         abort(404, message="Couldnt not find video...")

# def abort_if_video_exist(video_id):
#     """
#         cancels request for creating a video with an existing video id
#     """
#     if video_id in videos:
#         abort(409, message="Video already exist with that ID...")

# making a class that is a resource a dnthis resource has methods we can override on
# this lets us handle a GET PUT DELETE ... requrest

# using request object from flask gives us information about data sent from the client
class HelloWorld(Resource):
    def get(self, name):
        # returns json serializable objects/ basically python objects 
        return names[name]

# resource fields define how an instance from a model should be serialized
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'likes': fields.Integer,
    'views': fields.Integer
}

class Video(Resource):
    # this serializes the return result or response
    @marshal_with(resource_fields)
    def get(self, video_id):
        # abort_if_video_id_nonexistent(video_id)
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="Could not find video with that id...")
        return result

    # create a video in this endpoint 
    # return value "video" is an object that is serialized with the code below
    @marshal_with(resource_fields)
    def put(self, video_id):

        result = VideoModel.query.filter_by(id=video_id).first()

        if result:
            abort(409, message="Provided id already exist...")
        # abort_if_video_exist(video_id)
        args = video_put_args.parse_args()

        # instantiate form or request values with Vidoe model
        video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
        
        # commit instantiated object to the db
        db.session.add(video) # temporary addition to db 
        db.session.commit() # permanenet addition to db
        
        return video, 201

    @marshal_with(resource_fields)
    def patch(self, video_id):
        args = video_update_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        
        if not result:
            abort(400, message="Video does not exist, can't update...")
        
        # create instance with schema model
        if args['name']:
            result.name = args['name']
        if args['likes']:
            result.likes = args['likes']
        if args['views']:
            result.views = args['views']

        # updated_video = VideoModel(id=video_id, name=update_name, likes=update_likes, views=update_views)

        # db.session.add(updated_video)
        db.session.commit()

        return result



    # def delete(self, video_id):
    #     # abort_if_video_id_nonexistent(video_id)
    #     del videos[video_id]
    #     return '', 204

# register the class as a resource
# adding the resource to the api and making it accessible through a url or path
api.add_resource(HelloWorld, "/helloworld/<string:name>")
api.add_resource(Video, '/video/<int:video_id>')

if __name__ == "__main__":
    app.run(debug=True)