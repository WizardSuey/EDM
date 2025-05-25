from EDM import create_app, socketio

if __name__ == '__main__':
    app = create_app(config='prod')
    print(app.url_map)
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'], allow_unsafe_werkzeug=True)
