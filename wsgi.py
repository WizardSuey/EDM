from EDM import create_app, socketio

if __name__ == '__main__':
    app = create_app()
    print(app.url_map)
    socketio.run(app, host=app.config['HOST'], port=app.config['PORT'])